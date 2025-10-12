"""Configuration management with Dynaconf"""

from pathlib import Path
from dynaconf import Dynaconf, Validator
from pydantic import BaseModel, Field


def load_settings(config_file: str = None, env_file: str = None) -> Dynaconf:
    """
    Load configuration with precedence: CLI > ENV > File > Defaults
    
    Small, focused function - does one thing well.
    """
    settings = Dynaconf(
        envvar_prefix="AICL",
        settings_files=['~/.aicl/config.yaml', '.aicl.yaml', 'aicl.yaml'],
        environments=True,
        load_dotenv=True,
        merge_enabled=True,
        validators=[
            Validator('runtime.mode', is_in=['local', 'docker'], default='local'),
            Validator('runtime.docker_image', default='tofu-aicl:latest'),
            Validator('paths.state_dir', default='./terraform.tfstate.d'),
        ]
    )
    
    if config_file:
        settings.configure(SETTINGS_FILE_FOR_DYNACONF=str(config_file))
    
    if env_file:
        settings.configure(DOTENV_PATH_FOR_DYNACONF=str(env_file))
    
    settings.validators.validate()
    return settings


class RuntimeConfig(BaseModel):
    """Runtime configuration - separate model for clarity"""
    mode: str = "local"
    docker_image: str = "tofu-aicl:latest"
    provider_mode: str = "subprocess"


class PathsConfig(BaseModel):
    """Paths configuration - separate model"""
    state_dir: Path = Field(default=Path("./terraform.tfstate.d"))
    experiments_dir: Path = Field(default=Path("./experiments"))
    providers_dir: Path = Field(default=Path("./providers"))
