#!/bin/bash

# Railway Environment Variables Setup Script
# Run this after creating the backend service in Railway

set -e

echo "🚂 Setting up Railway environment variables for backend service"
echo ""

cd "$(dirname "$0")"

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI is not installed. Install it from https://railway.app/cli"
    exit 1
fi

# Check if service is linked
if ! railway status &> /dev/null; then
    echo "❌ No Railway project linked. Run: railway link --project ingenious-passion"
    exit 1
fi

echo "📝 Setting environment variables..."
echo ""

# Generate a secure secret key
SECRET_KEY=$(openssl rand -hex 32)

# Set variables (user will need to provide actual values)
echo "Please provide the following values:"
read -p "Mistral API Key: " MISTRAL_KEY
read -p "LinkedIn Email: " LINKEDIN_EMAIL
read -sp "LinkedIn Password: " LINKEDIN_PASS
echo ""

# Set all variables
railway variables --set "MISTRAL_API_KEY=$MISTRAL_KEY"
railway variables --set "LINKEDIN_EMAIL=$LINKEDIN_EMAIL"
railway variables --set "LINKEDIN_PASSWORD=$LINKEDIN_PASS"
railway variables --set "RATE_LIMIT_DELAY=45"
railway variables --set "FOLLOWUP_DAYS=7"
railway variables --set "SECRET_KEY=$SECRET_KEY"

echo ""
echo "✅ Environment variables set successfully!"
echo ""
echo "📋 Current variables:"
railway variables

echo ""
echo "📝 Next steps:"
echo "1. Make sure PostgreSQL database is added (railway add --database postgres)"
echo "2. Deploy: railway up"
echo "3. Run migrations: railway run alembic upgrade head"




