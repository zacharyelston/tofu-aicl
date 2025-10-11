"""
Provider Configuration Loader

Loads provider metadata from YAML config files instead of hardcoding in Python.
This follows the same pattern as the SQL config refactor - externalize config to data files.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class ProviderRuntime:
    """Provider runtime configuration"""
    entrypoint: str
    default_port: int
    mode: str  # "subprocess", "docker", or "both"


@dataclass
class ProviderDocker:
    """Provider Docker configuration"""
    image: str
    internal_port: int = 50051


@dataclass
class ProviderEnvironment:
    """Provider environment requirements"""
    required_vars: List[str] = field(default_factory=list)
    optional_vars: List[str] = field(default_factory=list)


@dataclass
class ProviderCapabilities:
    """Provider capabilities"""
    types: List[str] = field(default_factory=list)
    operations: List[str] = field(default_factory=list)


@dataclass
class ProviderModel:
    """Model metadata"""
    name: str
    type: str
    context_window: int
    cost_per_1k_input: float
    cost_per_1k_output: float
    quality_score: float


@dataclass
class ProviderHealth:
    """Health check configuration"""
    endpoint: str = "ValidateConfig"
    timeout_ms: int = 5000


@dataclass
class ProviderConfig:
    """
    Provider configuration loaded from YAML
    
    Replaces hardcoded ProviderMetadata in provider_registry.py
    """
    name: str
    display_name: str
    version: str
    source: str
    description: str
    runtime: ProviderRuntime
    docker: Optional[ProviderDocker]
    environment: ProviderEnvironment
    capabilities: ProviderCapabilities
    models: List[ProviderModel] = field(default_factory=list)
    health: ProviderHealth = field(default_factory=lambda: ProviderHealth())
    features: List[str] = field(default_factory=list)
    supported_formats: List[str] = field(default_factory=list)
    
    @property
    def container_image(self) -> Optional[str]:
        """Get Docker container image (for backward compatibility)"""
        return self.docker.image if self.docker else None
    
    @property
    def required_env_vars(self) -> List[str]:
        """Get required environment variables"""
        return self.environment.required_vars
    
    @property
    def default_port(self) -> int:
        """Get default port"""
        return self.runtime.default_port
    
    @property
    def entrypoint(self) -> str:
        """Get entrypoint script path"""
        return self.runtime.entrypoint
    
    def supports_mode(self, mode: str) -> bool:
        """Check if provider supports a specific runtime mode"""
        return self.runtime.mode == "both" or self.runtime.mode == mode
    
    def get_model(self, model_name: str) -> Optional[ProviderModel]:
        """Get model by name"""
        for model in self.models:
            if model.name == model_name:
                return model
        return None


class ProviderConfigLoader:
    """
    Load provider configurations from YAML files
    
    Usage:
        loader = ProviderConfigLoader()
        openai_config = loader.get("openai")
        all_providers = loader.list_all()
    """
    
    def __init__(self, providers_dir: Optional[Path] = None):
        """
        Initialize loader
        
        Args:
            providers_dir: Path to providers directory (defaults to project root)
        """
        if providers_dir is None:
            # Default to project root/providers
            providers_dir = Path(__file__).parent.parent.parent / "providers"
        
        self.providers_dir = Path(providers_dir)
        self._configs: Dict[str, ProviderConfig] = {}
        self._load_all_configs()
    
    def _load_all_configs(self):
        """Load all provider configs from YAML files"""
        if not self.providers_dir.exists():
            raise ValueError(f"Providers directory not found: {self.providers_dir}")
        
        # Find all provider directories with config.yaml
        for provider_dir in self.providers_dir.iterdir():
            if provider_dir.is_dir():
                config_file = provider_dir / "config.yaml"
                if config_file.exists():
                    try:
                        config = self._load_config_file(config_file)
                        self._configs[config.name] = config
                        # Also index by source for backward compatibility
                        self._configs[config.source] = config
                    except Exception as e:
                        print(f"Warning: Failed to load provider config {config_file}: {e}")
    
    def _load_config_file(self, config_file: Path) -> ProviderConfig:
        """Load a single provider config from YAML"""
        with open(config_file) as f:
            data = yaml.safe_load(f)
        
        provider_data = data['provider']
        
        # Parse runtime
        runtime_data = provider_data['runtime']
        runtime = ProviderRuntime(
            entrypoint=runtime_data['entrypoint'],
            default_port=runtime_data['default_port'],
            mode=runtime_data['mode']
        )
        
        # Parse Docker config (optional)
        docker = None
        if 'docker' in provider_data:
            docker_data = provider_data['docker']
            docker = ProviderDocker(
                image=docker_data['image'],
                internal_port=docker_data.get('internal_port', 50051)
            )
        
        # Parse environment
        env_data = provider_data.get('environment', {})
        environment = ProviderEnvironment(
            required_vars=env_data.get('required_vars', []),
            optional_vars=env_data.get('optional_vars', [])
        )
        
        # Parse capabilities
        cap_data = provider_data.get('capabilities', {})
        capabilities = ProviderCapabilities(
            types=cap_data.get('types', []),
            operations=cap_data.get('operations', [])
        )
        
        # Parse models (optional)
        models = []
        for model_data in provider_data.get('models', []):
            models.append(ProviderModel(
                name=model_data['name'],
                type=model_data['type'],
                context_window=model_data['context_window'],
                cost_per_1k_input=model_data['cost_per_1k_input'],
                cost_per_1k_output=model_data['cost_per_1k_output'],
                quality_score=model_data['quality_score']
            ))
        
        # Parse health (optional)
        health_data = provider_data.get('health', {})
        health = ProviderHealth(
            endpoint=health_data.get('endpoint', 'ValidateConfig'),
            timeout_ms=health_data.get('timeout_ms', 5000)
        )
        
        return ProviderConfig(
            name=provider_data['name'],
            display_name=provider_data['display_name'],
            version=provider_data['version'],
            source=provider_data['source'],
            description=provider_data['description'],
            runtime=runtime,
            docker=docker,
            environment=environment,
            capabilities=capabilities,
            models=models,
            health=health,
            features=provider_data.get('features', []),
            supported_formats=provider_data.get('supported_formats', [])
        )
    
    def get(self, name_or_source: str) -> Optional[ProviderConfig]:
        """
        Get provider config by name or source
        
        Args:
            name_or_source: Provider name (e.g., "openai") or source (e.g., "aicl/openai")
            
        Returns:
            ProviderConfig if found, None otherwise
        """
        return self._configs.get(name_or_source)
    
    def get_by_name(self, name: str) -> Optional[ProviderConfig]:
        """Get provider config by exact name"""
        return self._configs.get(name)
    
    def get_by_source(self, source: str) -> Optional[ProviderConfig]:
        """Get provider config by source"""
        return self._configs.get(source)
    
    def list_all(self) -> List[ProviderConfig]:
        """List all loaded provider configs"""
        # Return unique configs (avoid duplicates from name/source indexing)
        seen = set()
        unique_configs = []
        for config in self._configs.values():
            if config.name not in seen:
                seen.add(config.name)
                unique_configs.append(config)
        return unique_configs
    
    def list_by_type(self, provider_type: str) -> List[ProviderConfig]:
        """List providers by type (e.g., 'llm', 'embeddings')"""
        return [
            config for config in self.list_all()
            if provider_type in config.capabilities.types
        ]
    
    def get_model_catalog(self) -> Dict[str, List[ProviderModel]]:
        """Get catalog of all models across all providers"""
        catalog = {}
        for config in self.list_all():
            if config.models:
                catalog[config.name] = config.models
        return catalog
    
    def __len__(self) -> int:
        """Get number of unique providers"""
        return len(self.list_all())
    
    def __repr__(self):
        return f"<ProviderConfigLoader providers={len(self)} dir={self.providers_dir}>"


# Global instance for easy access
_loader = None

def get_provider_config_loader() -> ProviderConfigLoader:
    """Get global provider config loader instance"""
    global _loader
    if _loader is None:
        _loader = ProviderConfigLoader()
    return _loader
