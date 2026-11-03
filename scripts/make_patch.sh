#!/bin/sh
# Maintainer tool: print a unified diff turning <task_repo_dir> into <modified_dir>.
# usage: scripts/make_patch.sh tasks/tNN/repo /path/to/modified/copy > solution.patch
set -e
tmp=$(mktemp -d)
cp -r "$1" "$tmp/repo"
cd "$tmp/repo"
git init -q
git config core.autocrlf false
git add -A
git -c user.name=cf -c user.email=cf@example.invalid commit -qm base
find . -path ./.git -prune -o -type f -print | grep -v '^./.git' | xargs rm -f
cp -r "$2"/. .
find . -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
git add -A
git diff --cached
rm -rf "$tmp"
