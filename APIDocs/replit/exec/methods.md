# Exec API Methods

## Import
```javascript
import { exec } from '@replit/extensions';
```

## exec.spawn(options)
Spawn a process with streaming output.

```typescript
spawn(options: SpawnOptions): SpawnOutput
```

**Example:**
```javascript
const process = exec.spawn({
    command: 'python',
    args: ['script.py'],
    env: { PYTHONPATH: '/project' }
});

process.stdout.on('data', (data) => {
    console.log('Output:', data);
});

process.stderr.on('data', (data) => {
    console.error('Error:', data);
});
```

## exec.exec(command, options)
Execute command and return complete result.

```typescript
exec(command: string, options: { env: Record<string, string> }): Promise<ExecResult>
```

**Example:**
```javascript
const result = await exec.exec('ls -la', {
    env: { PATH: '/usr/bin' }
});

console.log('Exit code:', result.exitCode);
console.log('Output:', result.stdout);
console.log('Errors:', result.stderr);
```

## Types
- **SpawnOptions**: Configuration for spawning processes
- **SpawnOutput**: Streaming process output interface
- **ExecResult**: Complete execution result with exit code and output