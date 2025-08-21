from typing import Annotated, Any, Dict, List
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage

from ..agents.outliner import build_outliner_agent
from ..agents.research import build_research_agent
from ..agents.math import build_math_agent
from ..agents.critic import build_critic_agent
from ..agents.writer import build_writer_agent


class SupState(dict):
    """État du workflow avec tous les outputs"""
    messages: Annotated[List[Any], add_messages]
    o_json: str = ""
    r_json: str = ""
    m_json: str = ""
    c_json: str = ""
    final_md: str = ""


def extract_content(result: Dict) -> str:
    """Extrait le contenu du dernier message"""
    if "messages" in result and result["messages"]:
        last_msg = result["messages"][-1]
        if hasattr(last_msg, "content"):
            return str(last_msg.content)
        elif isinstance(last_msg, dict) and "content" in last_msg:
            return str(last_msg["content"])
    return ""


def build_workflow():
    graph = StateGraph(SupState)
    
    outliner = build_outliner_agent()
    research = build_research_agent()
    math = build_math_agent()
    critic = build_critic_agent()
    writer = build_writer_agent()

    def run_outliner(state: SupState) -> Dict:
        """Génère l'outline du rapport"""
        messages = state.get("messages", [])
        user_request = ""
        for msg in messages:
            if hasattr(msg, "type") and msg.type == "human":
                user_request = msg.content
                break
            elif isinstance(msg, dict) and msg.get("role") == "user":
                user_request = msg.get("content", "")
                break
        
        prompt = (
            "Produis un JSON d'outline DÉTAILLÉ pour un rapport complet.\n"
            "Format: {\"title\": str, \"sections\": [{\"h2\": str, \"h3\": [str,...]}]}\n"
            "Minimum 7 H2, 3-4 H3 par section, en français.\n"
            f"Requête: {user_request}"
        )
        
        result = outliner.invoke({"messages": [HumanMessage(content=prompt)]})
        o_json = extract_content(result)
        
        return {
            "messages": result.get("messages", []),
            "o_json": o_json
        }

    def run_research(state: SupState) -> Dict:
        """Collecte les données et informations"""
        o_json = state.get("o_json", "")
        
        data = """
            DONNÉES 2024:
            - PIB USA: 28,000 milliards USD
            - PIB New York: 2,200 milliards USD
            - Population USA: 335 millions
            - Population NY: 19.5 millions
            - Secteurs NY: Finance 30%, Immobilier 15%, Tech 12%, Santé 10%
            - Croissance NY 2023-2024: 4.8%
            - PIB NY 2023: 2,100 milliards
            - PIB NY 2022: 2,000 milliards
            """
        
        prompt = (
            "Synthétise les données en JSON détaillé:\n"
            "{\"key_points\": [8+ points], \"figures\": [{\"name\", \"value\", \"unit\", \"year\"}], "
            "\"assumptions\": [...], \"limitations\": [...]}\n"
            f"{data}\n"
            f"Outline: {o_json}"
        )
        
        result = research.invoke({"messages": [HumanMessage(content=prompt)]})
        r_json = extract_content(result)
        
        return {
            "messages": result.get("messages", []),
            "r_json": r_json
        }

    def run_math(state: SupState) -> Dict:
        """Effectue tous les calculs"""
        r_json = state.get("r_json", "")
        
        prompt = (
            "Calcule TOUT. Format JSON:\n"
            "{\"computations\": [{\"label\", \"formula\", \"result\"}], \"notes\": [...]}\n"
            "Calculs requis:\n"
            "- Part NY/USA: (2200/28000)*100\n"
            "- PIB/habitant NY et USA\n"
            "- Ratio PIB/hab NY vs USA\n"
            "- Part population NY/USA\n"
            "- Croissance 2023-2024\n"
            f"Data: {r_json}"
        )
        
        result = math.invoke({"messages": [HumanMessage(content=prompt)]})
        m_json = extract_content(result)
        
        return {
            "messages": result.get("messages", []),
            "m_json": m_json
        }

    def run_critic(state: SupState) -> Dict:
        """Vérifie la qualité"""
        prompt = (
            "Vérifie tout. JSON:\n"
            "{\"blocking_issues\": [], \"warnings\": [...], \"suggested_fixes\": [...]}\n"
            f"Outline: {state.get('o_json', '')[:500]}\n"
            f"Research: {state.get('r_json', '')[:500]}\n"
            f"Math: {state.get('m_json', '')[:500]}"
        )
        
        result = critic.invoke({"messages": [HumanMessage(content=prompt)]})
        c_json = extract_content(result)
        
        return {
            "messages": result.get("messages", []),
            "c_json": c_json
        }

    def run_writer(state: SupState) -> Dict:
        """Rédige le rapport final"""
        o_json = state.get("o_json", "")
        r_json = state.get("r_json", "")
        m_json = state.get("m_json", "")
        c_json = state.get("c_json", "")
        
        messages = state.get("messages", [])
        user_request = ""
        for msg in messages:
            if hasattr(msg, "type") and msg.type == "human":
                user_request = msg.content
                break
            elif isinstance(msg, dict) and msg.get("role") == "user":
                user_request = msg.get("content", "")
                break
        
        prompt = f"""
MISSION: Rédiger un RAPPORT COMPLET ET DÉTAILLÉ en Markdown basé sur les données fournies.

CONTEXTE DE LA REQUÊTE:
{user_request}

STRUCTURE OBLIGATOIRE (minimum 25 paragraphes au total):

# [Utiliser le titre depuis l'outline JSON]

## Résumé exécutif
Rédige 3-4 paragraphes avec:
- Les points clés de l'analyse
- Les chiffres principaux (si disponibles)
- Les conclusions majeures
- Les perspectives identifiées

## Table des matières
Liste complète avec numérotation de toutes les sections

## Données clés
Tableau markdown avec TOUS les indicateurs pertinents disponibles dans les données:
| Indicateur | Valeur | Description | Source/Année |
|------------|--------|-------------|--------------|
[Adapter selon les données disponibles]

## Méthodologie et hypothèses
2-3 paragraphes détaillant:
- Sources des données utilisées
- Méthodes d'analyse appliquées
- Hypothèses retenues
- Période couverte

## Analyse détaillée
DÉVELOPPER CHAQUE section H2/H3 de l'outline avec:
- Minimum 2 paragraphes substantiels par H2
- Intégration de TOUS les chiffres disponibles
- Analyses et interprétations pertinentes
- Mise en contexte appropriée

[SUIVRE LA STRUCTURE DE L'OUTLINE JSON]
Pour chaque H2 dans l'outline:
- Créer un ## avec le titre H2
- Pour chaque H3, créer un ### avec développement détaillé
- Intégrer les données pertinentes du research et math JSON

## Analyse approfondie
3-4 paragraphes supplémentaires sur:
- Points saillants de l'analyse
- Corrélations identifiées
- Tendances observées
- Facteurs d'influence

## Perspectives et projections
2-3 paragraphes sur:
- Évolutions attendues
- Scénarios possibles
- Opportunités identifiées
- Risques potentiels

## Recommandations stratégiques
Au moins 6 recommandations détaillées avec justifications:
1. **[Recommandation]**: [Justification détaillée]
2. **[Recommandation]**: [Justification détaillée]
[Continuer selon le contexte]

## Limites et considérations méthodologiques
2 paragraphes sur:
- Limites des données disponibles
- Contraintes méthodologiques
- Points d'attention
- Zones d'incertitude

## Conclusion
2-3 paragraphes de synthèse:
- Récapitulatif des points clés
- Réponse à la question initiale
- Perspectives futures
- Message final

## Annexes

### A. Détails techniques
- Formules utilisées (si applicable)
- Calculs détaillés (depuis math JSON)
- Méthodologie approfondie

### B. Sources et références
- Sources des données
- Références utilisées
- Notes méthodologiques

### C. Données complémentaires
- Tableaux additionnels
- Informations supplémentaires pertinentes

DONNÉES DISPONIBLES POUR LA RÉDACTION:
Outline (structure à suivre): {o_json}
Research (données et points clés): {r_json}
Math (calculs effectués): {m_json}
Critic (points d'attention): {c_json}

EXIGENCES FORMELLES:
✓ Adapter COMPLÈTEMENT le contenu à la requête utilisateur
✓ Utiliser le titre fourni dans l'outline JSON
✓ Suivre la structure H2/H3 de l'outline
✓ Intégrer TOUTES les données disponibles
✓ **Gras** pour les éléments importants
✓ *Italique* pour les termes techniques
✓ Listes à puces pour énumérations
✓ Tableaux pour données structurées
✓ Citations > pour points clés
✓ Code ` pour formules
✓ Minimum 25 paragraphes substantiels
✓ Ton professionnel et analytique

IMPORTANT: Le rapport doit traiter EXACTEMENT du sujet demandé par l'utilisateur, PAS d'un autre sujet.
"""
        
        result = writer.invoke({"messages": [HumanMessage(content=prompt)]})
        final_md = extract_content(result)
        
        # Nettoyer le markdown si entouré de ```markdown
        if final_md.startswith("```markdown"):
            final_md = final_md[11:]
        if final_md.endswith("```"):
            final_md = final_md[:-3]
        
        return {
            "messages": result.get("messages", []),
            "final_md": final_md.strip()
        }

    # On Ajoute les nœuds
    graph.add_node("outliner", run_outliner)
    graph.add_node("research", run_research)
    graph.add_node("math", run_math)
    graph.add_node("critic", run_critic)
    graph.add_node("writer", run_writer)

    # Supervision par edges (implémentation implicite)
    graph.set_entry_point("outliner")
    graph.add_edge("outliner", "research")
    graph.add_edge("research", "math")
    graph.add_edge("math", "critic")
    graph.add_edge("critic", "writer")
    graph.add_edge("writer", END)

    checkpointer = InMemorySaver()
    app = graph.compile(checkpointer=checkpointer)
    
    return app