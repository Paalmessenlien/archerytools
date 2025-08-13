#!/bin/bash
# Quick production fix script - reverts the problematic form schema commit

set -e

echo "🚨 Emergency Production Fix - Reverting Form Schema Changes"
echo "========================================================="

echo "📋 Current git status:"
git status --porcelain

echo ""
echo "📝 Recent commits:"
git log --oneline -5

echo ""
echo "🔄 Reverting commit 4617e23 (Fix equipment form schema API column name mismatch)"
echo "This will restore production compatibility while we set up unified development environment"

read -p "Continue with revert? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Revert cancelled"
    exit 1
fi

# Revert the problematic commit
git revert --no-edit 4617e23

echo "✅ Commit reverted successfully"
echo ""
echo "📤 Pushing revert to production..."
git push

echo ""
echo "🎉 Production fix completed!"
echo ""
echo "📋 Next steps:"
echo "1. Verify production is working: curl https://archerytool.online/api/health"
echo "2. Use new unified development environment: ./start-docker-dev.sh start"
echo "3. Test equipment form schema in development before next production push"

echo ""
echo "🐳 To start unified development environment:"
echo "   ./start-docker-dev.sh start"