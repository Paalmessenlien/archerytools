#!/bin/bash
# Quick Production Git Pull Fix
# Simple one-liner to fix divergent branches issue

echo "🚀 Quick Production Git Fix"
echo "=========================="

# The issue is likely just a git configuration problem
# This is the safest approach for production
echo "Setting merge strategy and pulling..."

git pull --no-rebase

echo "✅ Git pull completed"
echo ""
echo "📋 Verify status:"
git status --short

echo ""
echo "🎉 Production update complete!"
echo "📍 Next: Test the application and restart services if needed"