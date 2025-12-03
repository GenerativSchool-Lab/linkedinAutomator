# Railway Setup Status

## ✅ Completed

1. **Project Linked**: ingenious-passion
2. **Backend Service Created**: backend service is active
3. **Environment Variables Set**:
   - ✅ `RATE_LIMIT_DELAY=45`
   - ✅ `FOLLOWUP_DAYS=7`
   - ✅ `SECRET_KEY` (generated securely)

## ⏳ Still Needed (Requires Your Input)

### 1. Add PostgreSQL Database
The database addition requires interactive input. Run:
```bash
cd backend
railway add --database postgres
```
Then select "Database" when prompted.

**OR** add via Railway dashboard:
- Go to https://railway.app/project/ingenious-passion
- Click "New" → "Database" → "Add PostgreSQL"

### 2. Set Sensitive Environment Variables
You need to set these with your actual values:
```bash
cd backend
railway variables --set "MISTRAL_API_KEY=your-actual-mistral-api-key"
railway variables --set "LINKEDIN_EMAIL=your-actual-email@example.com"
railway variables --set "LINKEDIN_PASSWORD=your-actual-password"
```

**Note**: The `DATABASE_URL` will be automatically set by Railway when you add PostgreSQL.

### 3. Deploy
Once all variables are set:
```bash
cd backend
railway up
```

### 4. Run Database Migrations
After deployment:
```bash
cd backend
railway run alembic upgrade head
```

## 📋 Quick Command Reference

```bash
# Set remaining variables
cd backend
railway variables --set "MISTRAL_API_KEY=your-key"
railway variables --set "LINKEDIN_EMAIL=your-email"
railway variables --set "LINKEDIN_PASSWORD=your-password"

# View all variables
railway variables

# Deploy
railway up

# Run migrations
railway run alembic upgrade head

# View logs
railway logs

# Get service URL
railway domain
```

## 🔗 Useful Links

- Railway Dashboard: https://railway.app/project/ingenious-passion
- Service Status: Run `railway status` in backend directory



