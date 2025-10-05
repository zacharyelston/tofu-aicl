# Data API - Repl Methods

## data.currentRepl(args)
Get information about current workspace.

```typescript
currentRepl(args: ReplDataInclusion): Promise<{ repl: Repl }>
```

**Example:**
```javascript
const { repl } = await data.currentRepl({
    includeFiles: true,
    includeOwner: true
});
console.log('Current Repl:', repl.title);
console.log('Language:', repl.language);
console.log('File count:', repl.files?.length);
```

## data.replById(args)
Get Repl information by ID.

```typescript
replById(args: { id: string } & ReplDataInclusion): Promise<{ repl: Repl }>
```

**Example:**
```javascript
const { repl } = await data.replById({
    id: "repl-id-here",
    includeFiles: true
});
```

## data.replByUrl(args)
Get Repl information by URL.

```typescript
replByUrl(args: { url: string } & ReplDataInclusion): Promise<{ repl: Repl }>
```

**Example:**
```javascript
const { repl } = await data.replByUrl({
    url: "https://replit.com/@user/project-name",
    includeMetadata: true
});
```