from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from ..llm.azure import make_azure_llm

def build_critic_agent():
    model = make_azure_llm(temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a QA reviewer for French reports. Read the prior agents' outputs (outline, research synthesis, math results).\n"
         "Return a compact JSON with:\n"
         "{{ \"blocking_issues\": [str,...], \"warnings\": [str,...], \"suggested_fixes\": [str,...] }}\n"
         "Rules:\n"
         "- Flag missing numbers that were requested.\n"
         "- Flag unverifiable claims.\n"
         "- Suggest concrete fixes (short, actionable).\n"),
        MessagesPlaceholder("messages"),
    ])
    return create_react_agent(model=model, tools=[], prompt=prompt, name="critic_agent")
