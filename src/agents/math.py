from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from ..llm.azure import make_azure_llm

def build_math_agent():
    model = make_azure_llm(temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a careful math agent. Input will contain any numbers to compute.\n"
         "Return ONLY a JSON with the following shape:\n"
         "{{\"computations\": [{{\"label\": str, \"formula\": str, \"result\": str}}], \"notes\": [str,...]}}\n"
         "If required numbers are missing, return an empty computations list and a note explaining what's missing."),
        MessagesPlaceholder("messages"),
    ])
    return create_react_agent(model=model, tools=[], prompt=prompt, name="math_agent")
