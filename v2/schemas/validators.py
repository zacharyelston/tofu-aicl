"""
Configuration Validators

Validation functions for YAML configs using schema definitions.
"""

from typing import Dict, Any
from .models import (
    ProviderSchema,
    ProviderRuntimeSchema,
    ProviderDockerSchema,
    ProviderEnvironmentSchema,
    ProviderCapabilitiesSchema,
    ModelSchema,
    ExperimentSchema,
    ExperimentVariableSchema,
    RuntimeMode,
    ModelType
)


class ValidationError(Exception):
    """Raised when validation fails"""
    pass


def validate_provider_config(data: Dict[str, Any]) -> ProviderSchema:
    """
    Validate provider configuration
    
    Args:
        data: Provider config dict from YAML
        
    Returns:
        ProviderSchema instance
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        # Extract provider data
        provider_data = data.get('provider', {})
        
        # Build runtime schema
        runtime_data = provider_data.get('runtime', {})
        runtime = ProviderRuntimeSchema(
            entrypoint=runtime_data.get('entrypoint', ''),
            default_port=runtime_data.get('default_port', 0),
            mode=RuntimeMode(runtime_data.get('mode', 'subprocess'))
        )
        
        # Build Docker schema (optional)
        docker = None
        if 'docker' in provider_data:
            docker_data = provider_data['docker']
            docker = ProviderDockerSchema(
                image=docker_data.get('image', ''),
                internal_port=docker_data.get('internal_port', 50051)
            )
        
        # Build environment schema
        env_data = provider_data.get('environment', {})
        environment = ProviderEnvironmentSchema(
            required_vars=env_data.get('required_vars', []),
            optional_vars=env_data.get('optional_vars', [])
        )
        
        # Build capabilities schema
        cap_data = provider_data.get('capabilities', {})
        capabilities = ProviderCapabilitiesSchema(
            types=cap_data.get('types', []),
            operations=cap_data.get('operations', [])
        )
        
        # Build provider schema
        schema = ProviderSchema(
            name=provider_data.get('name', ''),
            display_name=provider_data.get('display_name', ''),
            version=provider_data.get('version', ''),
            source=provider_data.get('source', ''),
            description=provider_data.get('description', ''),
            runtime=runtime,
            docker=docker,
            environment=environment,
            capabilities=capabilities
        )
        
        # Validate
        schema.validate()
        return schema
        
    except (ValueError, KeyError) as e:
        raise ValidationError(f"Provider config validation failed: {e}") from e


def validate_model_config(data: Dict[str, Any]) -> ModelSchema:
    """
    Validate model configuration
    
    Args:
        data: Model config dict from YAML
        
    Returns:
        ModelSchema instance
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        schema = ModelSchema(
            id=data.get('id', ''),
            name=data.get('name', ''),
            display_name=data.get('display_name', ''),
            provider=data.get('provider', ''),
            type=ModelType(data.get('type', 'chat')),
            context_window=data.get('context_window', 0),
            cost_per_1k_input=data.get('cost_per_1k_input', 0.0),
            cost_per_1k_output=data.get('cost_per_1k_output', 0.0),
            quality_score=data.get('quality_score', 0.0),
            capabilities=data.get('capabilities', []),
            dimensions=data.get('dimensions'),
            reliability_score=data.get('reliability_score')
        )
        
        # Validate
        schema.validate()
        return schema
        
    except (ValueError, KeyError) as e:
        raise ValidationError(f"Model config validation failed: {e}") from e


def validate_experiment_config(data: Dict[str, Any]) -> ExperimentSchema:
    """
    Validate experiment configuration
    
    Args:
        data: Experiment config dict from YAML
        
    Returns:
        ExperimentSchema instance
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        # Build variable schemas
        variables = []
        for var_data in data.get('variables', []):
            var = ExperimentVariableSchema(
                name=var_data.get('name', ''),
                type=var_data.get('type', ''),
                values=var_data.get('values', []),
                min=var_data.get('min'),
                max=var_data.get('max'),
                step=var_data.get('step')
            )
            variables.append(var)
        
        # Build experiment schema
        schema = ExperimentSchema(
            name=data.get('name', ''),
            description=data.get('description', ''),
            variables=variables
        )
        
        # Validate
        schema.validate()
        return schema
        
    except (ValueError, KeyError) as e:
        raise ValidationError(f"Experiment config validation failed: {e}") from e
