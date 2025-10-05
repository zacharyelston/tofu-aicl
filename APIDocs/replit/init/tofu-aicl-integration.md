# Init API - tofu-aicl Integration

## Provider Resource
```hcl
resource "replit_extension" "ai_workflow" {
  name = "AI Workflow Manager"
  initialization = {
    auto_start = true
    handshake_timeout = 5000
  }
}
```

## Provider Implementation
```python
def ApplyResourceChange(self, request, context):
    config = MessageToDict(request.config)

    init_script = f"""
    import {{ init }} from '@replit/extensions';
    const dispose = await init({{
        name: '{config["name"]}',
        version: '{config.get("version", "1.0.0")}'
    }});

    // Store dispose function globally
    window.tofuAiclDispose = dispose;
    """

    result = self._execute_in_replit(init_script)

    return provider_pb2.ApplyResourceChangeResponse(
        new_state=self._create_state(config, result)
    )
```

## Use Cases
- Bootstrap AI workflow extensions
- Initialize provider connections
- Set up event listeners for AI triggers
- Manage extension lifecycle