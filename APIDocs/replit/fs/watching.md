# Filesystem API - File Watching

## fs.watchFile(path, listeners, encoding)
Monitor file for changes.

```typescript
watchFile(path: string, listeners: WatchFileListeners<string>, encoding: "utf8" | "binary"): Promise<DisposerFunction>
```

**Permissions**: `read`

**Example:**
```javascript
const dispose = await fs.watchFile('/project/main.py', {
    onChange: (content) => {
        console.log('File changed:', content);
    },
    onError: (error) => {
        console.error('Watch error:', error);
    }
}, 'utf8');

// Stop watching
dispose();
```

## fs.watchDir(path, listeners)
Monitor directory for changes.

```typescript
watchDir(path: string, listeners: WatchDirListeners): Promise<DisposerFunction>
```

**Permissions**: `read`

**Example:**
```javascript
const dispose = await fs.watchDir('/project', {
    onChange: (event) => {
        console.log('Directory changed:', event);
    }
});
```

## fs.watchTextFile(path, listeners)
Monitor text file with advanced change tracking.

```typescript
watchTextFile(path: string, listeners: WatchTextFileListeners): Function
```

**Permissions**: `read`

**Features:**
- Line-by-line change detection
- Text diff tracking
- Real-time content updates