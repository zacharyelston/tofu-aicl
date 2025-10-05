# Editor API Methods

## Import
```javascript
import { editor } from '@replit/extensions';
```

## editor.getPreferences()
Get current editor preferences.

```typescript
getPreferences(): Promise<EditorPreferences>
```

**Example:**
```javascript
const prefs = await editor.getPreferences();
console.log('Font size:', prefs.fontSize);
console.log('Tab size:', prefs.tabSize);
console.log('Theme:', prefs.theme);
console.log('Indentation:', prefs.indentationType);
```

## EditorPreferences Type
```typescript
interface EditorPreferences {
    fontSize: number;
    tabSize: number;
    theme: string;
    indentationType: 'spaces' | 'tabs';
    wordWrap: boolean;
    lineNumbers: boolean;
    // Additional editor settings
}
```