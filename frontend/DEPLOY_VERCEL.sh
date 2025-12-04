#!/bin/bash

# Deploy to Vercel script
# Run this after code is pushed to GitHub

cd /Volumes/LaCie/Dev/LKprospectionAgent/frontend

echo "🚀 Setting up Vercel deployment..."
echo ""

# Remove any existing link
rm -rf .vercel

# Create new project
echo "Creating new Vercel project..."
vercel --yes

# Set environment variable
echo ""
echo "Setting environment variable..."
echo "https://backend-production-433a.up.railway.app" | vercel env add NEXT_PUBLIC_API_URL production

# Deploy to production
echo ""
echo "Deploying to production..."
vercel --prod

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Get your Vercel URL from the output above"
echo "2. Update backend CORS:"
echo "   cd ../backend"
echo "   railway variables --set \"ALLOWED_ORIGINS=https://your-app.vercel.app\""


