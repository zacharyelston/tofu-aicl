# Commands API Methods

## Import
```javascript
import { commands } from '@replit/extensions';
```

## commands.add(args)
Register a custom command.

```typescript
add(args: AddCommandArgs): void
```

**Example - Action Command:**
```javascript
commands.add({
    id: 'ai-generate-code',
    label: 'Generate Code with AI',
    description: 'Generate code using AI based on current context',
    type: 'action',
    handler: async () => {
        // AI code generation logic
        console.log('Generating AI code...');
    }
});
```

**Example - Context Command:**
```javascript
commands.add({
    id: 'ai-improve-function',
    label: 'Improve Function with AI',
    type: 'context',
    context: 'editor',
    handler: async (context) => {
        const selectedText = context.selection;
        // AI improvement logic
    }
});
```

## Command Types
- **Action Commands**: Global commands accessible from command palette
- **Context Commands**: Context-sensitive commands for specific areas
- **File Handler Commands**: Commands for specific file types

## Command Configuration
- `id`: Unique command identifier
- `label`: Display name in command palette
- `description`: Optional description
- `type`: Command type ('action', 'context', etc.)
- `handler`: Function to execute when command is triggered