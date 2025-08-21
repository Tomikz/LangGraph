from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from ..llm.azure import make_azure_llm

def build_outliner_agent():
    model = make_azure_llm(temperature=0.1)
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are an outline planner for executive reports in French.\n"
         "TASK: Given a French user request, output ONLY a compact JSON with this shape (escape braces shown):\n"
         "{{ \"title\": str,\n"
         "  \"sections\": [ {{ \"h2\": str, \"h3\": [str, ...] }}, ... ] }}\n"
         "Rules:\n"
         "- h2 count between 5 and 8.\n"
         "- h3 per h2 between 2 and 4.\n"
         "- Keep titles short and informative.\n"),
        MessagesPlaceholder("messages"),
    ])
    return create_react_agent(model=model, tools=[], prompt=prompt, name="outliner_agent")
