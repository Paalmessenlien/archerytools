#!/bin/bash
# Production Git Synchronization Fix Script
# Safely resolves divergent branches on production server

set -e

echo "🔧 Production Git Synchronization Fix"
echo "====================================="

echo "📋 Current git status:"
git status --porcelain

echo ""
echo "📝 Recent local commits:"
git log --oneline -3 2>/dev/null || echo "No local commits found"

echo ""
echo "📝 Remote commits:"
git log --oneline -3 origin/main 2>/dev/null || echo "Cannot fetch remote commits"

echo ""
echo "🔍 Checking for divergence..."
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u} 2>/dev/null || echo "no-remote")
BASE=$(git merge-base @ @{u} 2>/dev/null || echo "no-base")

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "✅ Branches are already in sync"
elif [ "$LOCAL" = "$BASE" ]; then
    echo "📥 Local branch is behind, safe to fast-forward"
    echo "Running: git pull --ff-only"
    git pull --ff-only
elif [ "$REMOTE" = "$BASE" ]; then
    echo "📤 Local branch is ahead, need to push"
    echo "⚠️  This shouldn't happen on production server"
else
    echo "🔀 Branches have diverged, need to reconcile"
    echo ""
    echo "💡 Recommended approach for production:"
    echo "1. Stash any local changes"
    echo "2. Pull with merge strategy"
    echo "3. Re-apply stashed changes if needed"
    
    # Check if there are local changes
    if [[ -n $(git status --porcelain) ]]; then
        echo ""
        echo "📦 Stashing local changes..."
        git stash push -m "Production local changes $(date '+%Y-%m-%d %H:%M:%S')"
        echo "✅ Local changes stashed"
    fi
    
    echo ""
    echo "🔄 Pulling with merge strategy..."
    git pull --no-rebase
    
    # Check if there are stashed changes to restore
    if git stash list | grep -q "Production local changes"; then
        echo ""
        echo "📦 Attempting to restore stashed changes..."
        if git stash pop; then
            echo "✅ Successfully restored local changes"
        else
            echo "⚠️  Conflicts detected in stashed changes"
            echo "Manual resolution may be required"
            echo "Use 'git status' to check conflicts"
            echo "Use 'git stash drop' to discard stashed changes if not needed"
        fi
    fi
fi

echo ""
echo "📊 Final status:"
git status --short

echo ""
echo "🎉 Git synchronization completed!"
echo ""
echo "📋 Next steps:"
echo "1. Verify application is working: curl https://archerytool.online/api/health"
echo "2. Restart services if needed: ./start-unified.sh ssl archerytool.online"