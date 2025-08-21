from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from ..llm.azure import make_azure_llm

def build_writer_agent():
    model = make_azure_llm(temperature=0.2)
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a senior technical writer. Build a COMPLETE French report in Markdown.\n"
         "Inputs: outline JSON, research JSON, math JSON, critic JSON.\n"
         "Sections attendues (Markdown):\n"
         "# Titre du rapport\n"
         "## Résumé exécutif\n"
         "## Table des matières\n"
         "## Données clés (table)\n"
         "## Méthodologie et hypothèses\n"
         "## Analyse détaillée (suivre H2/H3 de l'outline)\n"
         "## Recommandations\n"
         "## Limites et points d'attention\n"
         "## Annexes\n"
         "Règles:\n"
         "- Insère le titre proposé par outliner_agent comme H1.\n"
         "- Intègre les chiffres du math JSON quand présents; sinon indique clairement qu'ils manquent.\n"
         "- Mentionne qu'aucune recherche web n'a été effectuée (Azure LLM only).\n"
         "- Ton: professionnel, concis, actionnable."),
        MessagesPlaceholder("messages"),
    ])
    return create_react_agent(model=model, tools=[], prompt=prompt, name="writer_agent")
