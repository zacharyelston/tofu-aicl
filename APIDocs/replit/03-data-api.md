# Replit Extensions Data API

## Overview
The Data API provides access to Replit's GraphQL API, allowing extensions to retrieve user information, Repl metadata, and other platform data. This is essential for understanding the context of the current workspace and user.

## Key Features
- **User Information**: Access current user and other user profiles
- **Repl Metadata**: Get information about current and other Repls
- **GraphQL Integration**: Direct access to Replit's internal data
- **Rich Data Types**: Comprehensive user and Repl objects with detailed information

## Usage
```javascript
import { data } from '@replit/extensions';
```

## Methods

### data.currentUser(args)
Retrieves information about the currently authenticated user.

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

### data.userById(args)
Retrieves user information by user ID.

```typescript
userById(args: { id: number } & UserDataInclusion): Promise<{ user: User }>
```

### data.userByUsername(args)
Retrieves user information by username.

```typescript
userByUsername(args: { username: string } & UserDataInclusion): Promise<{ userByUsername: User }>
```

### data.currentRepl(args)
Gets information about the current Repl workspace.

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
```

### data.replById(args)
Retrieves Repl information by ID.

```typescript
replById(args: { id: string } & ReplDataInclusion): Promise<{ repl: Repl }>
```

### data.replByUrl(args)
Retrieves Repl information by URL.

```typescript
replByUrl(args: { url: string } & ReplDataInclusion): Promise<{ repl: Repl }>
```

## Types
- **CurrentUser**: Extended user object with preferences and settings
- **User**: Standard user object with profile information
- **Repl**: Repl object with metadata, files, and ownership information
- **UserDataInclusion**: Options for including additional user data
- **ReplDataInclusion**: Options for including additional Repl data
- **CurrentUserDataInclusion**: Options specific to current user queries

## Integration with tofu-aicl

The Data API would be extremely valuable for a Replit provider in tofu-aicl, enabling context-aware AI workflows:

```hcl
# Get current workspace context
data "replit_current_repl" "workspace" {
  include_files = true
  include_owner = true
  include_metadata = true
}

# Get current user information
data "replit_current_user" "developer" {
  include_preferences = true
  include_profile = true
}

# Create AI workflow based on workspace context
resource "openrouter_model" "context_aware_ai" {
  model = "anthropic/claude-3.5-sonnet"

  # Use workspace context in AI prompt
  prompt = templatefile("ai_prompt.txt", {
    repl_title = data.replit_current_repl.workspace.title
    repl_language = data.replit_current_repl.workspace.language
    user_name = data.replit_current_user.developer.username
    file_count = length(data.replit_current_repl.workspace.files)
  })
}

# Deploy AI-generated code back to Repl
resource "replit_file_deployment" "ai_output" {
  repl_id = data.replit_current_repl.workspace.id

  files = {
    for file in resource.openrouter_model.context_aware_ai.output.files :
    file.name => file.content
  }

  # Preserve ownership and permissions
  owner_id = data.replit_current_user.developer.id
}
```

## Provider Implementation
```python
class ReplitProvider(provider_pb2_grpc.ProviderServicer):
    def _get_workspace_context(self):
        """Get current workspace and user context"""
        context_script = """
        import { data } from '@replit/extensions';

        const [userResult, replResult] = await Promise.all([
            data.currentUser({
                includePreferences: true,
                includeProfile: true
            }),
            data.currentRepl({
                includeFiles: true,
                includeOwner: true,
                includeMetadata: true
            })
        ]);

        return {
            user: userResult.user,
            repl: replResult.repl,
            context: {
                workspace_id: replResult.repl.id,
                workspace_title: replResult.repl.title,
                language: replResult.repl.language,
                file_count: replResult.repl.files?.length || 0,
                owner: replResult.repl.owner.username,
                created_at: replResult.repl.timeCreated
            }
        };
        """

        return self._execute_in_replit(context_script)

    def ReadResource(self, request, context):
        if request.type_name == "replit_current_repl":
            workspace_context = self._get_workspace_context()

            state = provider_pb2.ResourceState(
                id=workspace_context['repl']['id'],
                type="replit_current_repl",
                status="active"
            )

            state.attributes.update({
                "title": workspace_context['repl']['title'],
                "language": workspace_context['repl']['language'],
                "owner": workspace_context['repl']['owner']['username'],
                "file_count": len(workspace_context['repl'].get('files', [])),
                "created_at": workspace_context['repl']['timeCreated'],
                "url": workspace_context['repl']['url']
            })

            return provider_pb2.ReadResourceResponse(state=state)
```

## Use Cases for AI Workflows

### 1. Context-Aware Code Generation
```javascript
// Get current project context
const { repl } = await data.currentRepl({ includeFiles: true });
const { user } = await data.currentUser({ includePreferences: true });

// Generate AI prompt with context
const prompt = `
Generate ${repl.language} code for project "${repl.title}"
User preferences: ${user.preferences.theme}, ${user.preferences.fontSize}
Existing files: ${repl.files.map(f => f.name).join(', ')}
`;
```

### 2. Collaborative AI Workflows
```javascript
// Get team members from Repl collaborators
const { repl } = await data.currentRepl({ includeCollaborators: true });

// Create AI workflow for each collaborator
for (const collaborator of repl.collaborators) {
    const { user } = await data.userById({ id: collaborator.id });
    // Generate personalized AI tasks
}
```

### 3. Project Analysis and Recommendations
```javascript
// Analyze current project structure
const { repl } = await data.currentRepl({
    includeFiles: true,
    includeMetadata: true
});

// Use AI to analyze and recommend improvements
const analysis = await aiModel.analyze({
    project_type: repl.language,
    file_structure: repl.files,
    project_size: repl.size,
    last_modified: repl.timeUpdated
});
```

## Security and Privacy
- **User Consent**: Always respect user privacy when accessing profile data
- **Data Minimization**: Only request the data you actually need
- **Secure Storage**: Never store sensitive user data locally
- **Rate Limiting**: Be mindful of API rate limits when making multiple requests