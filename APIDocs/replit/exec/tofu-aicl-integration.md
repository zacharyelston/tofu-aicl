# Exec API - tofu-aicl Integration

## Provider Resource
```hcl
resource "replit_command_execution" "ai_script" {
  command = "python"
  args = ["ai_generated_script.py"]

  environment = {
    OPENAI_API_KEY = var.openai_key
    PYTHONPATH = "/project"
  }

  # Wait for file to be written first
  depends_on = [replit_file.ai_script]
}
```

## Provider Implementation
```python
def ApplyResourceChange(self, request, context):
    config = MessageToDict(request.config)

    if request.type_name == "replit_command_execution":
        exec_script = f"""
        import {{ exec }} from '@replit/extensions';

        const result = await exec.exec('{config["command"]} {" ".join(config.get("args", []))}', {{
            env: {json.dumps(config.get("environment", {}))}
        }});

        return {{
            exitCode: result.exitCode,
            stdout: result.stdout,
            stderr: result.stderr,
            success: result.exitCode === 0
        }};
        """

        result = self._execute_in_replit(exec_script)

        state = provider_pb2.ResourceState(
            id=f"exec-{uuid.uuid4().hex[:8]}",
            type="replit_command_execution",
            status="completed" if result.get('success') else "failed"
        )

        state.attributes.update({
            "command": config["command"],
            "exit_code": result.get('exitCode', -1),
            "stdout": result.get('stdout', ''),
            "stderr": result.get('stderr', ''),
            "executed_at": datetime.utcnow().isoformat()
        })

        return provider_pb2.ApplyResourceChangeResponse(new_state=state)
```

## Use Cases
- Execute AI-generated scripts
- Run build commands for generated code
- Execute tests on AI-created applications
- Run deployment scripts