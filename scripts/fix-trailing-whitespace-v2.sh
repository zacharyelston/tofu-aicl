#!/bin/bash

# Fix Trailing Whitespace Script v2
# More robust approach using perl for cross-platform compatibility

set -e

echo "🧹 Fixing trailing whitespace in all files (v2)..."

# Get list of all tracked files
files=$(git ls-files)

# Counter for files processed
count=0

# Process each file
for file in $files; do
    if [[ -f "$file" ]]; then
        # Use perl to remove trailing whitespace (works on macOS)
        perl -pi -e 's/[ \t]+$//' "$file"
        
        # Remove trailing blank lines at end of file
        perl -pi -e 'chomp if eof' "$file"
        
        ((count++))
    fi
done

echo "✅ Processed $count files"
echo "📝 Run 'git diff --check' to verify no trailing whitespace"
echo "💾 Run 'git add -A && git commit -m \"Fix trailing whitespace\"' to commit"
