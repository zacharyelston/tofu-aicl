# Themes API Methods

## Import
```javascript
import { themes } from '@replit/extensions';
```

## themes.getCurrentTheme()
Get current theme information.

```typescript
getCurrentTheme(): Promise<ThemeVersion>
```

**Example:**
```javascript
const theme = await themes.getCurrentTheme();
console.log('Current theme:', theme.name);
console.log('Color scheme:', theme.colorScheme); // 'light' or 'dark'
```

## themes.getCurrentThemeValues()
Get current theme color values.

```typescript
getCurrentThemeValues(): Promise<ThemeValuesGlobal>
```

**Example:**
```javascript
const values = await themes.getCurrentThemeValues();
console.log('Background color:', values.background);
console.log('Text color:', values.foreground);
console.log('Accent color:', values.accent);
```

## themes.onThemeChange(callback)
Listen for theme changes.

```typescript
onThemeChange(callback: OnThemeChangeListener): Promise<DisposerFunction>
```

**Example:**
```javascript
const dispose = await themes.onThemeChange((newTheme) => {
    console.log('Theme changed to:', newTheme.name);
    // Update UI accordingly
});

// Stop listening
dispose();
```

## themes.onThemeChangeValues(callback)
Listen for theme value changes.

```typescript
onThemeChangeValues(callback: OnThemeChangeValuesListener): Promise<DisposerFunction>
```

**Example:**
```javascript
const dispose = await themes.onThemeChangeValues((newValues) => {
    console.log('New colors:', newValues);
    // Update component styles
});
```