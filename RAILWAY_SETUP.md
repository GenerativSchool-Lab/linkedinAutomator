# Railway Setup Instructions

## Project: ingenious-passion

The project is already linked. Complete the following steps:

## Step 1: Add PostgreSQL Database

Run this command interactively:
```bash
railway add --database postgres
```

Or add it via Railway dashboard:
1. Go to https://railway.app/project/ingenious-passion
2. Click "New" → "Database" → "Add PostgreSQL"

## Step 2: Create Backend Service

The backend service needs to be created. You can do this via:

**Option A: Railway Dashboard (Recommended)**
1. Go to https://railway.app/project/ingenious-passion
2. Click "New" → "GitHub Repo" (if you've pushed to GitHub)
   OR "New" → "Empty Service"
3. If using GitHub, select your repository
4. Set the root directory to `backend/`

**Option B: Railway CLI (Interactive)**
```bash
cd backend
railway service
# Select "Create new service" and name it "backend"
```

## Step 3: Set Environment Variables

Once the service is created, set these environment variables in Railway dashboard:

### Required Variables:
- `MISTRAL_API_KEY` - Your Mistral AI API key
- `LINKEDIN_EMAIL` - Your LinkedIn email
- `LINKEDIN_PASSWORD` - Your LinkedIn password
- `RATE_LIMIT_DELAY` - Delay between actions (default: 45)
- `FOLLOWUP_DAYS` - Days to wait before follow-up (default: 7)
- `SECRET_KEY` - Secret key for encryption (generate a secure random string)

### Database Variable:
- `DATABASE_URL` - This is automatically set by Railway when you add PostgreSQL
  - It will be in the format: `postgresql://postgres:password@host:port/railway`

### How to Set Variables:

**Via Railway Dashboard:**
1. Go to your service in Railway dashboard
2. Click on "Variables" tab
3. Add each variable with its value

**Via Railway CLI:**
```bash
cd backend
railway variables set MISTRAL_API_KEY=your-key-here
railway variables set LINKEDIN_EMAIL=your-email@example.com
railway variables set LINKEDIN_PASSWORD=your-password
railway variables set RATE_LIMIT_DELAY=45
railway variables set FOLLOWUP_DAYS=7
railway variables set SECRET_KEY=$(openssl rand -hex 32)
```

## Step 4: Deploy

Once everything is configured:

**Via Railway Dashboard:**
- Railway will auto-deploy when you push to your connected GitHub repo
- Or click "Deploy" in the dashboard

**Via Railway CLI:**
```bash
cd backend
railway up
```

## Step 5: Get Database URL

After adding PostgreSQL, get the connection string:
```bash
railway variables
# Look for DATABASE_URL
```

Or in the dashboard:
1. Click on your PostgreSQL service
2. Go to "Variables" tab
3. Copy the `DATABASE_URL` value
4. Add it to your backend service variables (if not automatically linked)

## Step 6: Run Migrations

After deployment, run database migrations:
```bash
railway run alembic upgrade head
```

Or connect to the deployed service and run:
```bash
railway shell
alembic upgrade head
```

## Verification

Check that everything is working:
1. Visit your Railway service URL (shown in dashboard)
2. Check `/health` endpoint: `https://your-service.railway.app/health`
3. Check logs in Railway dashboard for any errors



