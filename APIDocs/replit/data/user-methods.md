# Data API - User Methods

## Import
```javascript
import { data } from '@replit/extensions';
```

## data.currentUser(args)
Get information about currently authenticated user.

```typescript
currentUser(args: CurrentUserDataInclusion): Promise<{ user: CurrentUser }>
```

**Example:**
```javascript
const { user } = await data.currentUser({
    includePreferences: true,
    includeProfile: true
});
console.log('Current user:', user.username);
```

## data.userById(args)
Get user information by ID.

```typescript
userById(args: { id: number } & UserDataInclusion): Promise<{ user: User }>
```

**Example:**
```javascript
const { user } = await data.userById({
    id: 12345,
    includeProfile: true
});
```

## data.userByUsername(args)
Get user information by username.

```typescript
userByUsername(args: { username: string } & UserDataInclusion): Promise<{ userByUsername: User }>
```

**Example:**
```javascript
const { userByUsername } = await data.userByUsername({
    username: "developer123",
    includeProfile: true
});
```