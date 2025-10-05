# Filesystem API - Directory Operations

## fs.readDir(path)
List directory contents.

```typescript
readDir(path: string): Promise<{ children: DirectoryChildNode[], error: string }>
```

**Permissions**: `read`

**Example:**
```javascript
const result = await fs.readDir('/project');
if ('children' in result) {
    result.children.forEach(child => {
        console.log(`${child.type}: ${child.name}`);
    });
}
```

## fs.createDir(path)
Create new directory.

```typescript
createDir(path: string): Promise<{ error: null | string, success: boolean }>
```

**Permissions**: `read`, `write-exec`

**Example:**
```javascript
const result = await fs.createDir('/project/new-folder');
if (result.success) {
    console.log('Directory created successfully');
}
```

## fs.deleteDir(path)
Delete directory and contents.

```typescript
deleteDir(path: string): Promise<{} | { error: string }>
```

**Permissions**: `read`, `write-exec`

**Warning**: This recursively deletes all contents.