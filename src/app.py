import sys
import uuid
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

from langchain_core.messages import BaseMessage
from .graph.supervisor import build_workflow


def _msg_to_preview(msg: Any) -> Tuple[str, str]:
    """
    Normalise un message (objet LangChain ou dict) en (role/type, texte).
    Gère aussi le cas où content est une liste (format structuré).
    """
    def _list_to_text(items: Iterable[Any]) -> str:
        parts = []
        for it in items:
            if isinstance(it, dict):
                parts.append(str(it.get("text") or it.get("content") or it))
            else:
                parts.append(str(it))
        return " ".join(parts)

    if isinstance(msg, BaseMessage):
        role = getattr(msg, "type", "assistant")
        content = getattr(msg, "content", "")
        if isinstance(content, list):
            return role, _list_to_text(content)
        return role, str(content)

    if isinstance(msg, dict):
        role = msg.get("role") or msg.get("type") or "assistant"
        content = msg.get("content")
        if isinstance(content, list):
            return role, _list_to_text(content)
        return role, str(content if content is not None else "")

    return "assistant", str(msg)


def save_report(content: str, query: str) -> str:
    """
    Sauvegarde le rapport dans un fichier Markdown.
    Retourne le chemin du fichier créé.
    """
    # Créer le dossier reports s'il n'existe pas
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
  
    query_short = "".join(c if c.isalnum() or c.isspace() else "_" for c in query[:50])
    query_short = "_".join(query_short.split())[:30]  
    
    filename = f"rapport_{query_short}_{timestamp}.md"
    filepath = reports_dir / filename
    
    metadata = f"""<!--
Rapport généré automatiquement
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Requête: {query}
-->

"""
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(metadata)
        f.write(content)
    
    return str(filepath)


def main(query: str, save_to_file: bool = True, open_file: bool = True):
    """
    Execute le workflow et génère le rapport.
    
    Args:
        query: La requête utilisateur
        save_to_file: Si True, sauvegarde le rapport dans un fichier
        open_file: Si True, ouvre le fichier après génération (Windows)
    """
    app = build_workflow()

    # Identifiant de thread requis par le checkpointer
    thread_id = f"cli-{uuid.uuid4()}"
    cfg: Dict[str, Any] = {
        "configurable": {
            "thread_id": thread_id,
            "recursion_limit": 8
        }
    }

    print("\n" + "="*60)
    print("GÉNÉRATION DU RAPPORT EN COURS...")
    print("="*60)
    
    final_report = None
    
    print("\nProgression:\n")
    
    # Stream pour suivre la progression
    for update in app.stream(
        {"messages": [{"role": "user", "content": query}]},
        subgraphs=True,
        config=cfg,
    ):
        ns = None
        payload = update
        if isinstance(update, tuple):
            ns, payload = update
        
        if isinstance(payload, dict):
            for node, state_update in payload.items():
                node_emojis = {
                    "outliner": "📝",
                    "research": "🔍",
                    "math": "🧮",
                    "critic": "✅",
                    "writer": "✍️"
                }
                
                if node in node_emojis:
                    print(f"  {node_emojis[node]} {node.capitalize()}: ", end="")
                    
                    if node == "writer" and isinstance(state_update, dict):
                        final_md = state_update.get("final_md", "")
                        if final_md:
                            final_report = final_md
                            print("✓ Rapport généré!")
                        else:
                            print("✓ Terminé")
                    else:
                        print("✓ Terminé")

    if not final_report:
        print("\nFinalisation...")
        result = app.invoke(
            {"messages": [{"role": "user", "content": query}]},
            config=cfg,
        )
    
        final_report = result.get("final_md", "")
        
        if not final_report:
            messages = result.get("messages", [])
            for msg in reversed(messages):
                role, text = _msg_to_preview(msg)
                if role in ("ai", "assistant") and text.strip().startswith("#"):
                    final_report = text
                    break

    print("\n" + "="*60)
    
    if final_report:
        print("\nAPERÇU DU RAPPORT (100 premiers caractères):")
        print("-" * 40)
        preview = final_report[:200].replace("\n", " ")
        print(preview + "...")
        print("-" * 40)
        
        if save_to_file:
            filepath = save_report(final_report, query)
            print(f"\nRAPPORT SAUVEGARDÉ AVEC SUCCÈS!")
            print(f"Fichier: {filepath}")
            
            file_size = os.path.getsize(filepath)
            print(f"Taille: {file_size:,} octets")
            
            lines = final_report.count('\n')
            words = len(final_report.split())
            print(f"Contenu: {lines} lignes, {words} mots")
            
            if open_file and sys.platform == "win32":
                try:
                    os.startfile(filepath)
                    print(f"Ouverture du fichier dans l'éditeur par défaut...")
                except Exception as e:
                    print(f"Impossible d'ouvrir automatiquement: {e}")
                    print(f"Vous pouvez l'ouvrir manuellement: {filepath}")
            elif open_file:
                print(f"\nPour ouvrir le fichier:")
                if sys.platform == "darwin": 
                    print(f"   open {filepath}")
                else:  
                    print(f"   xdg-open {filepath}")
        else:
            print("\nRAPPORT COMPLET:")
            print("="*60)
            print(final_report)
            print("="*60)
            
    else:
        print("\nERREUR: Aucun rapport n'a pu être généré.")
        print("   Vérifiez les logs ci-dessus pour identifier le problème.")
    
    print("\n✨ Processus terminé!")
    return final_report


if __name__ == "__main__":
    args = sys.argv[1:]
    
    save_file = "--no-save" not in args
    open_file = "--no-open" not in args
    
    
    args = [arg for arg in args if not arg.startswith("--")]
    
    user_query = " ".join(args) if args else \
        "Rédige un rapport complet sur la part du PIB de l'État de New York dans celui des États-Unis en 2024; inclure méthodologie, chiffres si disponibles, limites."
    
    print("\nConfiguration:")
    print(f"  - Sauvegarde fichier: {'Oui' if save_file else 'Non'}")
    print(f"  - Ouverture auto: {'Oui' if open_file else 'Non'}")
    print(f"\nRequête: {user_query[:100]}...")
    
    main(user_query, save_to_file=save_file, open_file=open_file)