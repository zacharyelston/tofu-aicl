# Session API Methods

## Import
```javascript
import { session } from '@replit/extensions';
```

## session.onActiveFileChange(callback)
Listen for active file changes.

```typescript
onActiveFileChange(callback: OnActiveFileChangeListener): Promise<DisposerFunction>
```

**Example:**
```javascript
const dispose = await session.onActiveFileChange((filePath) => {
    console.log('Active file changed to:', filePath);
    // Trigger AI analysis of new file
});

// Stop listening
dispose();
```

## session.getActiveFile()
Get currently active file path.

```typescript
getActiveFile(): Promise<string | null>
```

**Example:**
```javascript
const activeFile = await session.getActiveFile();
if (activeFile) {
    console.log('Currently editing:', activeFile);
} else {
    console.log('No file is currently active');
}
```

## Types
- **OnActiveFileChangeListener**: Callback function for file changes
- **DisposerFunction**: Function to stop listening for changes