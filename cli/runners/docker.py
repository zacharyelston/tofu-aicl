"""Docker runner - isolated in its own file"""

import subprocess
from pathlib import Path
from typing import List, Optional
from loguru import logger
from rich.console import Console

console = Console()


class DockerRunner:
    """
    Execute AICL in Docker containers
    
    Single class, single responsibility
    """
    
    def __init__(self, settings):
        self.settings = settings
        self.image = settings.runtime.docker_image
    
    def run(
        self,
        config_file: Path,
        workdir: Path,
        experiment_id: str,
        mounts: Optional[List[str]] = None
    ) -> int:
        """Execute configuration in Docker"""
        logger.info("Running in Docker", image=self.image)
        
        cmd = self._build_command(config_file, workdir, mounts)
        
        with console.status("[bold blue]Running Docker container..."):
            result = subprocess.run(cmd, capture_output=False, text=True)
        
        if result.returncode != 0:
            logger.error("Docker execution failed", code=result.returncode)
        
        return result.returncode
    
    def _build_command(
        self,
        config_file: Path,
        workdir: Path,
        mounts: Optional[List[str]]
    ) -> List[str]:
        """Build Docker command - private helper method"""
        cmd = ["docker", "run", "--rm"]
        
        # Environment
        if Path(".env").exists():
            cmd.extend(["--env-file", ".env"])
        
        # State directory mount
        state_dir = Path(self.settings.paths.state_dir)
        state_dir.mkdir(parents=True, exist_ok=True)
        cmd.extend(["-v", f"{state_dir.absolute()}:/app/terraform.tfstate.d"])
        
        # Custom mounts (safe access for Dynaconf)
        docker_config = getattr(self.settings, 'docker', None)
        docker_mounts = getattr(docker_config, 'mounts', []) if docker_config else []
        for mount in (mounts or docker_mounts):
            cmd.extend(["-v", mount])
        
        # Image and command
        cmd.extend([
            self.image,
            "python3", "run.py", str(config_file)
        ])
        
        logger.debug("Docker command", cmd=" ".join(cmd))
        return cmd
    
    def shell(self, workdir: Path = Path(".")):
        """Start interactive shell - separate method"""
        logger.info("Starting Docker shell")
        
        cmd = [
            "docker", "run", "--rm", "-it",
            "--env-file", ".env",
            "-v", f"{workdir.absolute()}:/app/work",
            "-w", "/app/work",
            "--entrypoint", "/bin/bash",
            self.image,
        ]
        
        subprocess.run(cmd)
