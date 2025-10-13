"""
Schema Definitions

Dataclass-based schema definitions for configuration validation.
These schemas ensure consistency across YAML configs and prevent drift.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class RuntimeMode(str, Enum):
    """Provider runtime modes"""
    SUBPROCESS = "subprocess"
    DOCKER = "docker"
    BOTH = "both"


class ModelType(str, Enum):
    """Model types"""
    CHAT = "chat"
    EMBEDDING = "embedding"
    COMPLETION = "completion"


@dataclass
class ProviderRuntimeSchema:
    """Provider runtime configuration schema"""
    entrypoint: str
    default_port: int
    mode: RuntimeMode
    
    def validate(self):
        """Validate runtime config"""
        if not 1 <= self.default_port <= 65535:
            raise ValueError(f"Invalid port {self.default_port}. Must be between 1 and 65535")
        
        if not self.entrypoint:
            raise ValueError("entrypoint cannot be empty")


@dataclass
class ProviderDockerSchema:
    """Provider Docker configuration schema"""
    image: str
    internal_port: int = 50051
    
    def validate(self):
        """Validate Docker config"""
        if not self.image:
            raise ValueError("Docker image cannot be empty")
        
        if not 1 <= self.internal_port <= 65535:
            raise ValueError(f"Invalid internal port {self.internal_port}")


@dataclass
class ProviderEnvironmentSchema:
    """Provider environment schema"""
    required_vars: List[str] = field(default_factory=list)
    optional_vars: List[str] = field(default_factory=list)
    
    def validate(self):
        """Validate environment config"""
        # Check for duplicates
        all_vars = self.required_vars + self.optional_vars
        if len(all_vars) != len(set(all_vars)):
            duplicates = [v for v in all_vars if all_vars.count(v) > 1]
            raise ValueError(f"Duplicate environment variables: {set(duplicates)}")


@dataclass
class ProviderCapabilitiesSchema:
    """Provider capabilities schema"""
    types: List[str] = field(default_factory=list)
    operations: List[str] = field(default_factory=list)
    
    def validate(self):
        """Validate capabilities"""
        if not self.types:
            raise ValueError("Provider must have at least one type")


@dataclass
class ProviderSchema:
    """Provider configuration schema"""
    name: str
    display_name: str
    version: str
    source: str
    description: str
    runtime: ProviderRuntimeSchema
    docker: Optional[ProviderDockerSchema]
    environment: ProviderEnvironmentSchema
    capabilities: ProviderCapabilitiesSchema
    
    def validate(self):
        """Validate complete provider config"""
        # Validate name format (lowercase, alphanumeric + underscore)
        if not self.name.replace('_', '').replace('-', '').isalnum():
            raise ValueError(f"Invalid provider name '{self.name}'. Must be alphanumeric with underscores/hyphens")
        
        # Validate source format
        if '/' not in self.source:
            raise ValueError(f"Invalid source '{self.source}'. Must be in format 'namespace/name'")
        
        # Validate version format (semantic versioning)
        parts = self.version.split('.')
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            raise ValueError(f"Invalid version '{self.version}'. Must be semantic version (e.g., '1.0.0')")
        
        # Validate nested schemas
        self.runtime.validate()
        if self.docker:
            self.docker.validate()
        self.environment.validate()
        self.capabilities.validate()
        
        # Check Docker requirement
        if self.runtime.mode in (RuntimeMode.DOCKER, RuntimeMode.BOTH):
            if not self.docker:
                raise ValueError(f"Docker config required for mode '{self.runtime.mode}'")


@dataclass
class ModelSchema:
    """Model configuration schema"""
    id: str
    name: str
    display_name: str
    provider: str
    type: ModelType
    context_window: int
    cost_per_1k_input: float
    cost_per_1k_output: float
    quality_score: float
    capabilities: List[str] = field(default_factory=list)
    dimensions: Optional[int] = None
    reliability_score: Optional[float] = None
    
    def validate(self):
        """Validate model config"""
        # Validate ID format
        if not self.id.replace('-', '').replace('_', '').replace('/', '').isalnum():
            raise ValueError(f"Invalid model ID '{self.id}'")
        
        # Validate costs
        if self.cost_per_1k_input < 0:
            raise ValueError(f"Invalid cost_per_1k_input: {self.cost_per_1k_input}")
        
        if self.cost_per_1k_output < 0:
            raise ValueError(f"Invalid cost_per_1k_output: {self.cost_per_1k_output}")
        
        # Validate quality score
        if not 0 <= self.quality_score <= 10:
            raise ValueError(f"Invalid quality_score: {self.quality_score}. Must be between 0 and 10")
        
        # Validate reliability score if present
        if self.reliability_score is not None:
            if not 0 <= self.reliability_score <= 10:
                raise ValueError(f"Invalid reliability_score: {self.reliability_score}. Must be between 0 and 10")
        
        # Validate context window
        if self.context_window <= 0:
            raise ValueError(f"Invalid context_window: {self.context_window}")
        
        # Validate dimensions for embedding models
        if self.type == ModelType.EMBEDDING:
            if self.dimensions is None or self.dimensions <= 0:
                raise ValueError(f"Embedding model must have positive dimensions")


@dataclass
class ExperimentVariableSchema:
    """Experiment variable schema"""
    name: str
    type: str  # chat_model, embedding_model, temperature, etc.
    values: List[any] = field(default_factory=list)
    min: Optional[float] = None
    max: Optional[float] = None
    step: Optional[float] = None
    
    def validate(self):
        """Validate experiment variable"""
        if not self.name:
            raise ValueError("Variable name cannot be empty")
        
        if not self.type:
            raise ValueError("Variable type cannot be empty")
        
        # Either values or range (min/max/step) must be provided
        has_values = len(self.values) > 0
        has_range = all([self.min is not None, self.max is not None, self.step is not None])
        
        if not (has_values or has_range):
            raise ValueError(f"Variable '{self.name}' must have either 'values' or 'min/max/step'")


@dataclass
class ExperimentSchema:
    """Experiment configuration schema"""
    name: str
    description: str
    variables: List[ExperimentVariableSchema] = field(default_factory=list)
    
    def validate(self):
        """Validate experiment config"""
        if not self.name:
            raise ValueError("Experiment name cannot be empty")
        
        if not self.variables:
            raise ValueError("Experiment must have at least one variable")
        
        # Validate all variables
        for var in self.variables:
            var.validate()
        
        # Check for duplicate variable names
        names = [v.name for v in self.variables]
        if len(names) != len(set(names)):
            duplicates = [n for n in names if names.count(n) > 1]
            raise ValueError(f"Duplicate variable names: {set(duplicates)}")
