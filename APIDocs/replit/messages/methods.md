# Messages API Methods

## Import
```javascript
import { messages } from '@replit/extensions';
```

## messages.showConfirm(str, length)
Show confirmation message.

```typescript
showConfirm(str: string, length: number): Promise<string>
```

**Example:**
```javascript
const messageId = await messages.showConfirm('AI workflow completed successfully!', 5000);
```

## messages.showError(str, length)
Show error message.

```typescript
showError(str: string, length: number): Promise<string>
```

**Example:**
```javascript
const messageId = await messages.showError('AI workflow failed: API key invalid', 10000);
```

## messages.showNotice(str, length)
Show informational notice.

```typescript
showNotice(str: string, length: number): Promise<string>
```

**Example:**
```javascript
const messageId = await messages.showNotice('Starting AI code generation...', 3000);
```

## messages.showWarning(str, length)
Show warning message.

```typescript
showWarning(str: string, length: number): Promise<string>
```

**Example:**
```javascript
const messageId = await messages.showWarning('AI model usage approaching limit', 7000);
```

## messages.hideMessage(id)
Hide specific message by ID.

```typescript
hideMessage(id: string): Promise<void>
```

## messages.hideAllMessages()
Hide all current messages.

```typescript
hideAllMessages(): Promise<void>
```

## Parameters
- `str`: Message text to display
- `length`: Display duration in milliseconds
- `id`: Message ID returned from show methods