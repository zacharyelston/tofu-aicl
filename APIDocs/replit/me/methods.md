# Me API Methods

## Import
```javascript
import { me } from '@replit/extensions';
```

## me.filePath()
Get file path for file handler extensions.

```typescript
filePath(): Promise<string | null>
```

**Example:**
```javascript
const filePath = await me.filePath();
if (filePath) {
    console.log('Extension opened with file:', filePath);
    // Process specific file with AI
} else {
    console.log('Extension not opened as file handler');
}
```

## Use Cases
- File-specific AI processing
- Context-aware extension behavior
- File type detection for AI workflows
- Custom file handler implementations