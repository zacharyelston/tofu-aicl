# Manifest Properties

## Basic Properties
```json
{
  "name": "string",
  "version": "string",
  "description": "string",
  "author": "string"
}
```

## Permissions
```json
{
  "permissions": ["read", "write-exec"],
  "scopes": [
    {
      "name": "filesystem",
      "description": "Access to read and write files"
    }
  ]
}
```

## File Handlers
```json
{
  "fileHandlers": [
    {
      "glob": "*.py",
      "page": "python-handler.html"
    }
  ]
}
```

## Tools
```json
{
  "tools": [
    {
      "name": "AI Code Generator",
      "page": "ai-tool.html"
    }
  ]
}
```

## Background Pages
```json
{
  "backgroundPage": {
    "page": "background.html",
    "persistent": true
  }
}
```

## Cover Images
```json
{
  "coverImages": [
    {
      "url": "cover-light.png",
      "theme": "light"
    },
    {
      "url": "cover-dark.png",
      "theme": "dark"
    }
  ]
}
```