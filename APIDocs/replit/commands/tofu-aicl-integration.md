# Commands API - tofu-aicl Integration

## Provider Resource
```hcl
resource "replit_command" "ai_workflow_trigger" {
  id = "ai-workflow-${var.workflow_name}"
  label = "Run AI Workflow: ${var.workflow_name}"
  description = "Execute AI workflow with current workspace context"

  type = "action"
  category = "AI Workflows"

  # Link to AI workflow resources
  workflow_resources = [
    resource.openrouter_model.code_generator.id,
    resource.pinecone_index.knowledge_base.id
  ]
}
```

## Provider Implementation
```python
def ApplyResourceChange(self, request, context):
    config = MessageToDict(request.config)

    if request.type_name == "replit_command":
        command_script = f"""
        import {{ commands }} from '@replit/extensions';

        commands.add({{
            id: '{config["id"]}',
            label: '{config["label"]}',
            description: '{config.get("description", "")}',
            type: '{config.get("type", "action")}',
            handler: async (context) => {{
                // Trigger tofu-aicl workflow
                const workflowResult = await fetch('/api/trigger-workflow', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        workflowId: '{config["id"]}',
                        context: context,
                        resources: {json.dumps(config.get("workflow_resources", []))}
                    }})
                }});

                const result = await workflowResult.json();
                console.log('Workflow executed:', result);

                return result;
            }}
        }});

        return {{ success: true, commandId: '{config["id"]}' }};
        """

        result = self._execute_in_replit(command_script)

        state = provider_pb2.ResourceState(
            id=config["id"],
            type="replit_command",
            status="registered"
        )

        state.attributes.update({
            "command_id": config["id"],
            "label": config["label"],
            "type": config.get("type", "action"),
            "registered_at": datetime.utcnow().isoformat()
        })

        return provider_pb2.ApplyResourceChangeResponse(new_state=state)
```

## Use Cases
- Trigger AI code generation from command palette
- Context-sensitive AI improvements
- Workflow automation commands
- AI-powered refactoring tools