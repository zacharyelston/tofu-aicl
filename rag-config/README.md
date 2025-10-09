# RAG Config Directory

This directory is for files you want to index in Pinecone for RAG queries.

## Usage

**Option 1: Use this directory**
- Copy or symlink files you want to index into this directory
- The script will recursively scan all files (excluding binary/cache files)
- Supports subdirectories for organization

**Option 2: Use RAG-files.txt**
- Create `RAG-files.txt` in project root
- List file paths (one per line, relative to project root)
- More explicit control over what gets indexed

**Option 3: Default list**
- If neither exists, uses hardcoded default list of core files

## Priority

1. **RAG-files.txt** (if exists) - Explicit file list
2. **rag-config/** (if exists) - Directory scan
3. **Default list** - Hardcoded core files

## Example Structure

```
rag-config/
├── core/
│   ├── parser.py
│   ├── evaluator.py
│   └── executor.py
├── docs/
│   ├── architecture.md
│   └── api-reference.md
└── examples/
    └── basic-usage.aicl
```

## Automation

You can populate this directory with automation:
```bash
# Copy specific files
cp src/aicl/*.py rag-config/

# Symlink entire directory
ln -s ../src/aicl rag-config/aicl

# Use find to copy matching files
find src -name "*.py" -exec cp {} rag-config/ \;
```

## Notes

- Binary files are automatically skipped (`.pyc`, `.so`, etc.)
- `__pycache__` directories are ignored
- Empty or very small files (<50 chars) are skipped during chunking
