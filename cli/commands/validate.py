"""Validate command - single responsibility"""

import json
from pathlib import Path
from loguru import logger

from cli.utils.output import console, show_syntax, print_error


def validate_command(config_file: Path) -> int:
    """
    Validate AICL configuration
    
    Only validates - doesn't run or modify
    """
    logger.info("Validating configuration", config=str(config_file))
    
    try:
        from src.aicl.parser import HCLParser
        
        with console.status("[bold yellow]Parsing configuration..."):
            parser = HCLParser(str(config_file))
            parsed = parser.parse()
        
        # Display result
        show_syntax(
            json.dumps(parsed, indent=2),
            language="json",
            title=f"✅ Valid Configuration: {config_file}"
        )
        
        logger.success("Configuration is valid", config=str(config_file))
        return 0
        
    except Exception as e:
        logger.error("Validation failed", error=str(e))
        print_error(f"Validation failed: {e}")
        return 1
