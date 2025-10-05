# Resource Lifecycle Flows

## Extension Initialization

```mermaid
sequenceDiagram
    participant E as Engine
    participant P as Provider
    participant JS as JS Bridge
    participant N as Node.js
    participant R as Replit API

    E->>P: ApplyResourceChange(replit_extension)
    activate P

    P->>P: Validate config<br/>(name, version, timeout)

    P->>JS: execute_js(init_script, timeout=5000)
    activate JS

    JS->>N: subprocess.run(node -e "...")
    activate N

    N->>R: init({name, version})
    activate R
    R->>R: Register extension
    R->>R: Perform handshake
    R-->>N: {success: true, dispose: fn}
    deactivate R

    N-->>JS: JSON: {success: true, ...}
    deactivate N

    JS->>JS: JSON.parse(result)
    JS-->>P: {success, dispose_fn}
    deactivate JS

    P->>P: Create Extension object<br/>Store dispose function

    P-->>E: new_state{id, status: "initialized"}
    deactivate P
```

**Key Steps:**
1. Engine requests extension creation
2. Provider validates config
3. JavaScript bridge spawns Node.js
4. Replit API performs handshake
5. Dispose function stored
6. State returned to engine

---

## Authentication Flow

```mermaid
sequenceDiagram
    participant E as Engine
    participant P as Provider
    participant JS as JS Bridge
    participant R as Replit API

    E->>P: ApplyResourceChange(auth_session)
    P->>P: Check extension exists

    alt Extension not initialized
        P-->>E: Error: FAILED_PRECONDITION
    else Extension ready
        P->>JS: execute_js(auth_script)
        JS->>R: auth.authenticate()
        R-->>JS: {user: {...}}
        JS->>R: auth.getAuthToken()
        R-->>JS: {token: "eyJ..."}
        JS-->>P: {user, token}

        P->>P: Create AuthSession<br/>Hash token

        P-->>E: new_state{user_id, username, token_hash}
    end
```

**Key Steps:**
1. Check extension prerequisite
2. Call authenticate() and getAuthToken()
3. Hash token for security
4. Return session state

---

## Data Source Flow

```mermaid
sequenceDiagram
    participant E as Engine
    participant P as Provider
    participant JS as JS Bridge
    participant R as Replit API

    E->>P: ReadDataSource(workspace_data)

    par Fetch User
        P->>JS: data.currentUser()
        JS->>R: currentUser()
        R-->>JS: {user: {...}}
    and Fetch Workspace
        P->>JS: data.currentRepl()
        JS->>R: currentRepl()
        R-->>JS: {repl: {...}}
    end

    P->>P: Merge data
    P-->>E: state{repl_id, title, user, ...}
```

**Key Steps:**
1. Parallel fetch (user + workspace)
2. Use Promise.all() for performance
3. Merge results
4. Return combined state

---

## Resource Destruction

```mermaid
sequenceDiagram
    participant E as Engine
    participant P as Provider
    participant JS as JS Bridge
    participant R as Replit API

    E->>P: DestroyResource(ext-id)
    activate P
    P->>JS: execute_js(dispose_script)
    activate JS
    JS->>R: dispose()
    R-->>JS: success
    JS-->>P: success
    deactivate JS
    P-->>E: Empty response
    deactivate P
```

**Key Steps:**
1. Call stored dispose function
2. Clean up Replit extension
3. Return success