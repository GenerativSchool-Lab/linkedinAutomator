#!/bin/bash

# Push to GitHub script
# This will prompt for your GitHub credentials

cd /Volumes/LaCie/Dev/LKprospectionAgent

echo "Pushing to GitHub..."
echo "Repository: https://github.com/GenerativSchool-Lab/linkedinAutomator.git"
echo ""
echo "You'll be prompted for:"
echo "  Username: Your GitHub username"
echo "  Password: Use a Personal Access Token (not your password)"
echo ""
echo "To create a token: https://github.com/settings/tokens"
echo ""

git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo "Repository: https://github.com/GenerativSchool-Lab/linkedinAutomator"
else
    echo ""
    echo "❌ Push failed. Make sure you have:"
    echo "  1. Created a Personal Access Token at https://github.com/settings/tokens"
    echo "  2. Used the token as your password (not your GitHub password)"
    echo "  3. Have write access to the repository"
fi
