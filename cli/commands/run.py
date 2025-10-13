"""Run command - isolated from other commands"""

from pathlib import Path
from typing import Optional, List
from loguru import logger

from cli.runners.docker import DockerRunner
from cli.runners.local import LocalRunner
from cli.utils.output import print_success


def run_command(
    config_file: Path,
    workdir: Path,
    experiment_id: str,
    docker: Optional[bool],
    mount: Optional[List[str]],
    settings
) -> int:
    """
    Run AICL configuration
    
    Orchestrates runners - doesn't do the work itself
    """
    logger.info("Starting run", config=str(config_file), experiment_id=experiment_id)
    
    # Determine execution mode
    use_docker = docker if docker is not None else settings.runtime.mode == "docker"
    
    # Delegate to appropriate runner
    if use_docker:
        runner = DockerRunner(settings)
        result = runner.run(config_file, workdir, experiment_id, mount)
    else:
        runner = LocalRunner(settings)
        result = runner.run(config_file, workdir, experiment_id)
    
    if result == 0:
        print_success("Execution complete!")
        logger.success("Run completed", experiment_id=experiment_id)
    
    return result
