# Auth API Methods

## Import
```javascript
import { experimental } from '@replit/extensions';
const { auth } = experimental;
```

## auth.getAuthToken()
Returns unique JWT token for authenticated user.

```typescript
getAuthToken(): Promise<string>
```

**Example:**
```javascript
const token = await auth.getAuthToken();
console.log('User token:', token);
```

## auth.verifyAuthToken(token)
Verifies JWT token and returns decoded payload.

```typescript
verifyAuthToken(token: string): Promise<{ payload: any, protectedHeader: any }>
```

**Example:**
```javascript
const verification = await auth.verifyAuthToken(token);
console.log('User ID:', verification.payload.userId);
```

## auth.authenticate()
Performs full user authentication.

```typescript
authenticate(): Promise<AuthenticateResult>
```

**Example:**
```javascript
const result = await auth.authenticate();
if (result.success) {
    console.log('Authenticated user:', result.user);
}
```