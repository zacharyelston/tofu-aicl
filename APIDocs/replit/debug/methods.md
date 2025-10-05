# Debug API Methods

## Import
```javascript
import { debug } from '@replit/extensions';
```

## debug.info(message)
Log informational message.

```typescript
info(message: string): void
```

**Example:**
```javascript
debug.info('AI workflow started successfully');
```

## debug.warn(message)
Log warning message.

```typescript
warn(message: string): void
```

**Example:**
```javascript
debug.warn('AI model approaching rate limit');
```

## debug.error(message)
Log error message.

```typescript
error(message: string): void
```

**Example:**
```javascript
debug.error('AI workflow failed: Invalid API key');
```

## debug.log(message)
General purpose logging.

```typescript
log(message: string): void
```

**Example:**
```javascript
debug.log('Processing file: ' + fileName);
```

## Best Practices
- Use appropriate log levels
- Include context in messages
- Avoid logging sensitive data
- Use structured logging for complex data