#!/bin/bash

# Quick Railway Setup Commands
# Copy and paste these commands one by one, or run this script

cd /Volumes/LaCie/Dev/LKprospectionAgent/backend

# 1. Link project (if not already linked)
railway link --project ingenious-passion

# 2. Add PostgreSQL database (interactive - will prompt)
railway add --database postgres

# 3. Create backend service (interactive - will prompt)
# Or do this via dashboard: https://railway.app/project/ingenious-passion
railway add --service backend

# 4. Set environment variables (replace with your actual values)
railway variables --set "MISTRAL_API_KEY=your-mistral-api-key-here"
railway variables --set "LINKEDIN_EMAIL=your-email@example.com"
railway variables --set "LINKEDIN_PASSWORD=your-password-here"
railway variables --set "RATE_LIMIT_DELAY=45"
railway variables --set "FOLLOWUP_DAYS=7"
railway variables --set "SECRET_KEY=$(openssl rand -hex 32)"

# 5. Deploy
railway up

# 6. Run database migrations
railway run alembic upgrade head

echo "✅ Setup complete! Check your Railway dashboard for the service URL."




