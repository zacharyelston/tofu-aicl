from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ProviderMetadata:
    name: str
    source: str
    version: str
    container_image: str
    description: str = ""

class ProviderRegistry:
    def __init__(self):
        self._providers: Dict[str, ProviderMetadata] = {}
        self._load_default_providers()

    def _load_default_providers(self):
        default_providers = [
            ProviderMetadata(
                name="file_loader",
                source="aicl/file_loader",
                version="1.0.0",
                container_image="aicl/file_loader:1.0.0",
                description="Load documents from filesystem"
            ),
            ProviderMetadata(
                name="text_splitter",
                source="aicl/text_splitter",
                version="1.0.0",
                container_image="aicl/text_splitter:1.0.0",
                description="Chunk text for embeddings"
            ),
            ProviderMetadata(
                name="openrouter",
                source="aicl/openrouter",
                version="1.0.0",
                container_image="aicl/openrouter:1.0.0",
                description="AI models via OpenRouter (embeddings, chat, query)"
            ),
            ProviderMetadata(
                name="pinecone",
                source="aicl/pinecone",
                version="1.0.0",
                container_image="aicl/pinecone:1.0.0",
                description="Vector database (upsert, query, index)"
            ),
            ProviderMetadata(
                name="command_assertion",
                source="aicl/command_assertion",
                version="1.0.0",
                container_image="aicl/command_assertion:1.0.0",
                description="Validation and testing"
            ),
            ProviderMetadata(
                name="openai",
                source="aicl/openai",
                version="1.0.0",
                container_image="aicl/openai:1.0.0",
                description="OpenAI embeddings"
            ),
            ProviderMetadata(
                name="azure_openai",
                source="aicl/azure_openai",
                version="1.0.0",
                container_image="aicl/azure_openai:1.0.0",
                description="Azure OpenAI embeddings"
            ),
        ]

        for provider in default_providers:
            self.register(provider)

    def register(self, provider: ProviderMetadata):
        self._providers[provider.source] = provider
        self._providers[provider.name] = provider

    def get(self, source_or_name: str) -> Optional[ProviderMetadata]:
        return self._providers.get(source_or_name)

    def list_all(self) -> Dict[str, ProviderMetadata]:
        unique_providers = {}
        for provider in self._providers.values():
            if provider.source not in unique_providers:
                unique_providers[provider.source] = provider
        return unique_providers

    def get_container_image(self, source_or_name: str) -> Optional[str]:
        provider = self.get(source_or_name)
        return provider.container_image if provider else None

    def get_provider_name(self, source: str) -> Optional[str]:
        provider = self.get(source)
        return provider.name if provider else None

_global_registry = ProviderRegistry()

def get_registry() -> ProviderRegistry:
    return _global_registry