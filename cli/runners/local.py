"""Local runner - separated from Docker runner"""

import sys
import os
from pathlib import Path
from loguru import logger
from rich.console import Console

console = Console()


class LocalRunner:
    """
    Execute AICL locally
    
    Focused on local execution only
    """
    
    def __init__(self, settings):
        self.settings = settings
    
    def run(
        self,
        config_file: Path,
        workdir: Path,
        experiment_id: str
    ) -> int:
        """Execute configuration locally"""
        logger.info("Running locally", config=str(config_file))
        
        original_dir = Path.cwd()
        os.chdir(workdir)
        
        try:
            return self._execute_engine(config_file)
        finally:
            os.chdir(original_dir)
    
    def _execute_engine(self, config_file: Path) -> int:
        """Execute AICL engine - private method"""
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from src.aicl.core.engine import AICLEngine
            
            with console.status("[bold green]Running AICL engine..."):
                engine = AICLEngine(config_path=str(config_file))
                engine.run()
            
            return 0
            
        except Exception as e:
            logger.exception("Execution failed", error=str(e))
            console.print(f"[red]❌ Error:[/red] {e}")
            return 1
