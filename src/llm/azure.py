from langchain_openai import AzureChatOpenAI
from ..config import settings  

def make_azure_llm(temperature: float = 0) -> AzureChatOpenAI:
    az = settings.azure
    if not (az.api_key and az.endpoint and az.deployment and az.api_version):
        raise RuntimeError(
            "Variables Azure OpenAI manquantes. Renseigne AZURE_OPENAI_API_KEY, "
            "AZURE_OPENAI_API_BASE ou AZURE_OPENAI_ENDPOINT, "
            "AZURE_OPENAI_API_DEPLOYMENT_NAME, AZURE_OPENAI_API_VERSION."
        )
    return AzureChatOpenAI(
        azure_endpoint=az.endpoint,
        azure_deployment=az.deployment,
        api_version=az.api_version,
        api_key=az.api_key,
        temperature=temperature,
    )
