# Filesystem API - File Operations

## Import
```javascript
import { fs } from '@replit/extensions';
```

## fs.readFile(path, encoding)
Read file contents.

```typescript
readFile(path: string, encoding: null | "utf8" | "binary"): Promise<{ content: string } | { error: string }>
```

**Permissions**: `read`

**Example:**
```javascript
const result = await fs.readFile('/path/to/file.txt', 'utf8');
if ('content' in result) {
    console.log('File content:', result.content);
} else {
    console.error('Error:', result.error);
}
```

## fs.writeFile(path, content)
Write content to file.

```typescript
writeFile(path: string, content: string | Blob): Promise<{ success: boolean } | { error: string }>
```

**Permissions**: `read`, `write-exec`

## fs.deleteFile(path)
Delete a file.

```typescript
deleteFile(path: string): Promise<{} | { error: string }>
```

**Permissions**: `read`, `write-exec`

## fs.copyFile(from, to)
Copy file to new location.

```typescript
copyFile(path: string, to: string): Promise<{ error: null | string, success: boolean }>
```

**Permissions**: `read`, `write-exec`

## fs.move(from, to)
Move/rename file.

```typescript
move(path: string, to: string): Promise<{ error: null | string, success: boolean }>
```

**Permissions**: `read`, `write-exec`