# Push to GitHub

## Steps to Push Code

1. **Create the repository on GitHub:**
   - Go to https://github.com/new
   - Repository name: `linkedin-prospection-agent`
   - Make it Public or Private (your choice)
   - **Don't** initialize with README, .gitignore, or license
   - Click "Create repository"

2. **Push the code:**
   ```bash
   cd /Volumes/LaCie/Dev/LKprospectionAgent
   git remote add origin https://github.com/chyll/linkedin-prospection-agent.git
   git push -u origin main
   ```

   Or if you prefer SSH (if you have SSH keys set up):
   ```bash
   git remote add origin git@github.com:chyll/linkedin-prospection-agent.git
   git push -u origin main
   ```

3. **If authentication is needed:**
   - For HTTPS: Use a Personal Access Token (Settings > Developer settings > Personal access tokens)
   - For SSH: Set up SSH keys in GitHub

## After Pushing

Once the code is on GitHub, we can:
- Set up Vercel to deploy from GitHub
- Configure automatic deployments


