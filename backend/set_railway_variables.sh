#!/bin/bash
# Script to set Railway environment variables for LinkedIn Prospection Agent

echo "Setting Railway environment variables..."

# Navigate to backend directory
cd "$(dirname "$0")"

# Check if railway CLI is available
if ! command -v railway &> /dev/null; then
    echo "Error: Railway CLI not found. Please install it first:"
    echo "  npm i -g @railway/cli"
    echo "  railway login"
    exit 1
fi

# Set rate limiting variables
echo "Setting rate limiting variables..."
railway variables set RATE_LIMIT_DELAY=30
railway variables set MAX_CONNECTIONS_PER_DAY=20
railway variables set RETRY_DELAY_BASE=60
railway variables set MAX_RETRIES=3

# Set follow-up settings
echo "Setting follow-up settings..."
railway variables set FOLLOWUP_DAYS=7

# Display current variables
echo ""
echo "Current Railway variables:"
railway variables

echo ""
echo "Done! Variables have been set."
echo ""
echo "You can also set these manually:"
echo "  railway variables set RATE_LIMIT_DELAY=30"
echo "  railway variables set MAX_CONNECTIONS_PER_DAY=20"
echo "  railway variables set RETRY_DELAY_BASE=60"
echo "  railway variables set MAX_RETRIES=3"
echo "  railway variables set FOLLOWUP_DAYS=7"

