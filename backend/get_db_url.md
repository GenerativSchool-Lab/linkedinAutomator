# Getting DATABASE_URL from Railway

## Option 1: Railway Dashboard (Easiest)

1. Go to https://railway.app/project/ingenious-passion
2. Click on your PostgreSQL service
3. Go to the "Variables" tab
4. Look for `DATABASE_URL` or `POSTGRES_URL`
5. Copy the full connection string

It should look like:
```
postgresql://postgres:password@caboose.proxy.rlwy.net:5432/railway
```

## Option 2: Link Services in Railway

1. Go to your backend service in Railway dashboard
2. Click "Variables" tab
3. Click "New Variable" or "Reference Variable"
4. Select your PostgreSQL service
5. Select `DATABASE_URL` from the dropdown
6. Railway will automatically link it

## Option 3: Manual Construction

If you have the individual components:
- Host: `caboose.proxy.rlwy.net`
- Port: Usually `5432` for Railway PostgreSQL
- User: Usually `postgres`
- Password: From Railway PostgreSQL service variables
- Database: Usually `railway`

Format:
```
postgresql://postgres:PASSWORD@caboose.proxy.rlwy.net:5432/railway
```

Once you have the full DATABASE_URL, we can set it with:
```bash
cd backend
railway variables --set "DATABASE_URL=postgresql://..."
```



