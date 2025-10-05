# Init API Usage

## Basic Usage
```javascript
import { init } from '@replit/extensions';

const dispose = await init({
  // Optional initialization parameters
});
```

## With Error Handling
```javascript
try {
  const dispose = await init();
  console.log('Extension initialized successfully');

  // Store dispose function for cleanup
  window.extensionDispose = dispose;
} catch (error) {
  console.error('Failed to initialize extension:', error);
}
```

## Cleanup
```javascript
// When extension is unloaded or component unmounts
if (window.extensionDispose) {
  window.extensionDispose();
}
```