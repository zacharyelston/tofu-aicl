# Replit Extensions Init API

## Overview
The `init()` method is the foundation of every Replit extension. It initializes the extension, establishes a handshake with the Replit App, and sets up the communication channel.

## Key Features
- **Extension Initialization**: Establishes connection with Replit App
- **Handshake Protocol**: Ensures proper communication setup
- **Event Listener Management**: Adds and manages window event listeners
- **Cleanup Function**: Returns a disposer function for proper cleanup

## Usage
```javascript
import { init } from '@replit/extensions';

const dispose = await init({
  // Optional initialization parameters
});

// Later, when extension is unloaded
dispose(); // Removes event listeners
```

## Method Signature
```typescript
init(args: ReplitInitArgs): Promise<ReplitInitOutput>
```

## Types
- **ReplitInitArgs**: Configuration object for initialization
- **ReplitInitOutput**: Result object containing disposer function
- **HandshakeStatus**: Status of the handshake process

## Integration with tofu-aicl
This API would be essential for a Replit provider in tofu-aicl:

```hcl
resource "replit_extension" "ai_workflow" {
  name = "AI Workflow Manager"
  initialization = {
    auto_start = true
    handshake_timeout = 5000
  }
}
```

The provider would use the init API to:
1. Initialize the extension when the resource is created
2. Establish communication with the Replit workspace
3. Set up event listeners for workflow triggers
4. Provide cleanup when the resource is destroyed

## Provider Implementation
```python
def ApplyResourceChange(self, request, context):
    # Initialize Replit extension
    init_script = f"""
    import {{ init }} from '@replit/extensions';
    const dispose = await init({{
        name: '{config["name"]}',
        version: '{config.get("version", "1.0.0")}'
    }});
    """

    # Execute initialization script in Replit context
    result = self._execute_in_replit(init_script)

    return provider_pb2.ApplyResourceChangeResponse(
        new_state=self._create_state(config, result)
    )
```