from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from ..llm.azure import make_azure_llm

def build_research_agent():
    model = make_azure_llm(temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a research synthesizer with NO external browsing.\n"
         "TASK: Produce a JSON in French summarizing what is known from internal model knowledge only.\n"
         "Schema:\n"
         "{{ \"key_points\": [str,...],\n"
         "  \"figures\": [{{\"name\": str, \"value\": str, \"unit\": str, \"year\": str}}],\n"
         "  \"assumptions\": [str,...],\n"
         "  \"limitations\": [\"Pas d'accès au web; chiffres potentiellement datés\", ...] }}\n"
         "Rules:\n"
         "- If the user provides a DATA block (YAML/JSON) in the conversation, prefer those numbers.\n"
         "- If you are uncertain, put 'estimation' in value and add a limitation note.\n"),
        MessagesPlaceholder("messages"),
    ])
    return create_react_agent(model=model, tools=[], prompt=prompt, name="research_agent")
