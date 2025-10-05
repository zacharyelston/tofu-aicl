#!/bin/bash

# Fix Trailing Whitespace Script
# Removes trailing whitespace from all files in the repository

set -e

echo "🧹 Fixing trailing whitespace in all files..."

# Find all files tracked by git and remove trailing whitespace
git ls-files | while read -r file; do
    if [[ -f "$file" ]]; then
        # Use sed to remove trailing whitespace
        sed -i '' 's/[[:space:]]*$//' "$file"
    fi
done

# Remove trailing blank lines at end of files
git ls-files | while read -r file; do
    if [[ -f "$file" ]]; then
        # Remove trailing blank lines using awk
        awk '/^[[:space:]]*$/{p++;next} {for(i=0;i<p;i++)print ""; p=0; print}' "$file" > "$file.tmp" && mv "$file.tmp" "$file"
    fi
done

echo "✅ Trailing whitespace fixed in all files"
echo "📝 Run 'git diff' to see changes"
echo "💾 Run 'git add -A && git commit -m \"Fix trailing whitespace\"' to commit"
