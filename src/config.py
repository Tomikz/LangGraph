from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

load_dotenv()

class AzureSettings(BaseModel):
    api_key: str = Field(default_factory=lambda: os.getenv("AZURE_OPENAI_API_KEY", ""))
    api_base: str = Field(default_factory=lambda: os.getenv("AZURE_OPENAI_API_BASE", "")) 
    deployment: str = Field(default_factory=lambda: os.getenv("AZURE_OPENAI_API_DEPLOYMENT_NAME", ""))
    api_version: str = Field(default_factory=lambda: os.getenv("AZURE_OPENAI_API_VERSION", ""))

    @property
    def endpoint(self) -> str:
        return self.api_base

class AppSettings(BaseModel):
    azure: AzureSettings = Field(default_factory=AzureSettings)
    tavily_api_key: str = Field(default_factory=lambda: os.getenv("TAVILY_API_KEY", ""))

settings = AppSettings()
