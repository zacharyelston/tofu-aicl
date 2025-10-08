#!/usr/bin/env python3
"""
Debug script to understand the state structure
"""

import json
from src.aicl.state.manager import StateManager, ResourceState

# Create a mock state to understand the structure
state_manager = StateManager()
state_manager.load("debug-test")

# Add a mock resource similar to what loader_files would create
# Now using the AICL resource name as the ID
mock_resource = ResourceState(
    id="aicl_source",
    type="loader_files",
    provider="loader",
    attributes={"documents": ["file1.py", "file2.py"]},
    metadata={"created": "2025-10-06"}
)

state_manager.add_resource(mock_resource)

# Get the dictionary representation
all_resources = state_manager.get_all_resources_as_dict()

print("=== State Structure Debug ===")
print(json.dumps(all_resources, indent=2))

# Test the reference resolution path
reference = "resource.loader_files.aicl_source.attributes.documents"
parts = reference.split('.')[1:]  # Skip 'resource'
print(f"\nReference: {reference}")
print(f"Parts: {parts}")

# Try to traverse
current = all_resources
for i, part in enumerate(parts):
    print(f"Step {i+1}: Looking for '{part}' in {type(current)}")
    if isinstance(current, dict):
        print(f"Available keys: {list(current.keys())}")
        if part in current:
            current = current[part]
            print(f"Found: {current}")
        else:
            print(f"ERROR: '{part}' not found!")
            break
    else:
        print(f"ERROR: Cannot traverse non-dict for '{part}'")
        break
