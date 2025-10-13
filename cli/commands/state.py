"""State management commands - grouped by feature"""

import json
from loguru import logger

from cli.utils.output import console, create_resource_table, show_syntax, print_error


def list_state(experiment_id: str, settings) -> int:
    """List resources in state - focused function"""
    logger.info("Listing state", experiment_id=experiment_id)
    
    try:
        from src.aicl.state.manager import StateManager
        
        manager = StateManager(state_dir=str(settings.paths.state_dir))
        state = manager.load(experiment_id)
        
        # Use reusable table component
        table = create_resource_table(state.resources)
        console.print(table)
        
        logger.info("State listed", resource_count=len(state.resources))
        return 0
        
    except Exception as e:
        logger.error("Failed to list state", error=str(e))
        print_error(f"Error: {e}")
        return 1


def show_resource(resource_id: str, experiment_id: str, settings) -> int:
    """Show specific resource - focused function"""
    logger.info("Showing resource", resource_id=resource_id)
    
    try:
        from src.aicl.state.manager import StateManager
        
        manager = StateManager(state_dir=str(settings.paths.state_dir))
        manager.load(experiment_id)
        resource = manager.get_resource(resource_id)
        
        if not resource:
            print_error(f"Resource not found: {resource_id}")
            return 1
        
        # Display resource
        resource_dict = {
            "id": resource.id,
            "type": resource.type,
            "provider": resource.provider,
            "status": resource.status,
            "attributes": resource.attributes,
            "metadata": resource.metadata,
        }
        
        show_syntax(
            json.dumps(resource_dict, indent=2),
            language="json",
            title=f"🔍 Resource: {resource_id}"
        )
        
        return 0
        
    except Exception as e:
        logger.error("Failed to show resource", error=str(e))
        print_error(f"Error: {e}")
        return 1
