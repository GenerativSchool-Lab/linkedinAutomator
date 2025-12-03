#!/bin/bash

# Railway Setup Script for LinkedIn Prospection Agent
# Run this script to set up your Railway project

set -e

echo "🚂 Setting up Railway project: ingenious-passion"
echo ""

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI is not installed. Install it from https://railway.app/cli"
    exit 1
fi

# Navigate to backend directory
cd "$(dirname "$0")/backend"

echo "📦 Current status:"
railway status

echo ""
echo "📝 Next steps (some require interactive input):"
echo ""
echo "1. Add PostgreSQL database:"
echo "   railway add --database postgres"
echo ""
echo "2. Create backend service (via dashboard or):"
echo "   railway service"
echo ""
echo "3. Set environment variables:"
echo "   railway variables set MISTRAL_API_KEY=your-key"
echo "   railway variables set LINKEDIN_EMAIL=your-email"
echo "   railway variables set LINKEDIN_PASSWORD=your-password"
echo "   railway variables set RATE_LIMIT_DELAY=45"
echo "   railway variables set FOLLOWUP_DAYS=7"
echo "   railway variables set SECRET_KEY=\$(openssl rand -hex 32)"
echo ""
echo "4. Deploy:"
echo "   railway up"
echo ""
echo "5. Run migrations:"
echo "   railway run alembic upgrade head"
echo ""
echo "See RAILWAY_SETUP.md for detailed instructions."



