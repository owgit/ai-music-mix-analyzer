#!/bin/bash

# Create backup branch
git checkout -b backup_before_filter_branch

# Remove .cursor directory from history
git filter-branch --force --index-filter \
  "git rm -r --cached --ignore-unmatch .cursor" \
  --prune-empty --tag-name-filter cat -- --all

# Remove memory-bank directory from history
git filter-branch --force --index-filter \
  "git rm -r --cached --ignore-unmatch memory-bank" \
  --prune-empty --tag-name-filter cat -- --all

echo "Done! Both .cursor and memory-bank directories have been removed from git history."
echo "You can now run 'git push origin main --force' to update the remote repository."
echo "Be careful! Force pushing will rewrite history on the remote repository." 