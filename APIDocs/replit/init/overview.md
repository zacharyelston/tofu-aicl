# Init API Overview

## Purpose
Initialize Replit extensions and establish handshake with the Replit App.

## Method Signature
```typescript
init(args: ReplitInitArgs): Promise<ReplitInitOutput>
```

## Usage
```javascript
import { init } from '@replit/extensions';

const dispose = await init({
  // Optional initialization parameters
});

// Cleanup when extension unloads
dispose();
```

## Types
- **ReplitInitArgs**: Configuration object for initialization
- **ReplitInitOutput**: Result containing disposer function
- **HandshakeStatus**: Status of handshake process

## Key Features
- Extension-to-App communication setup
- Event listener management
- Proper cleanup mechanisms
- Handshake validation