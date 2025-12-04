# Vercel Deployment Guide

## After GitHub Repository is Ready

### 1. Create New Vercel Project

```bash
cd frontend
rm -rf .vercel  # Remove any existing link
vercel
```

When prompted:
- **Set up and deploy?** → Yes
- **Which scope?** → Select your account
- **Link to existing project?** → No
- **What's your project's name?** → `linkedin-prospection-agent` (or your preferred name)
- **In which directory is your code located?** → `./frontend` (or just `.` if you're in frontend directory)

### 2. Set Environment Variable

After project is created, set the API URL:

```bash
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://backend-production-433a.up.railway.app
```

Or via Vercel Dashboard:
1. Go to your project
2. Settings → Environment Variables
3. Add: `NEXT_PUBLIC_API_URL` = `https://backend-production-433a.up.railway.app`

### 3. Deploy

```bash
vercel --prod
```

### 4. Update Backend CORS

After deployment, get your Vercel URL and update backend:

```bash
cd backend
railway variables --set "ALLOWED_ORIGINS=https://your-app.vercel.app"
```

## Alternative: Deploy from GitHub

1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Set root directory to `frontend`
4. Add environment variable: `NEXT_PUBLIC_API_URL`
5. Deploy


