# Vercel Deployment Setup

## Configuration Files Created

1. **`.vercelignore`** (root) - Excludes backend and other files from Vercel deployment
2. **`frontend/vercel.json`** - Vercel configuration for Next.js

## Deployment Steps

### 1. Link to Vercel Project

```bash
cd frontend
vercel link
```

Or create a new project:
```bash
cd frontend
vercel
```

### 2. Set Environment Variable

Set the backend API URL in Vercel:

```bash
cd frontend
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://backend-production-433a.up.railway.app
```

Or via Vercel Dashboard:
1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add: `NEXT_PUBLIC_API_URL` = `https://backend-production-433a.up.railway.app`

### 3. Deploy

```bash
cd frontend
vercel --prod
```

## Important Notes

- Vercel will only deploy the `frontend/` directory (backend is ignored via `.vercelignore`)
- The frontend will make API calls directly to the Railway backend
- Make sure to update backend CORS to allow your Vercel domain after deployment

## Update Backend CORS

After getting your Vercel domain, update the backend CORS:

```bash
cd backend
# Update app/main.py to include your Vercel domain in allow_origins
```

Or set it via environment variable if you prefer.

