# Environment Variables Setup

## Backend Environment Variables

Create a `.env` file in the `backend/` directory with the following variables:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/linkedin_agent
MISTRAL_API_KEY=your-mistral-api-key
LINKEDIN_EMAIL=your-email@example.com
LINKEDIN_PASSWORD=your-password
RATE_LIMIT_DELAY=45
FOLLOWUP_DAYS=7
SECRET_KEY=your-secret-key-change-in-production
```

## Getting Your Mistral API Key

1. Sign up at https://mistral.ai/
2. Navigate to your API keys section
3. Create a new API key
4. Copy the key and add it to your `.env` file as `MISTRAL_API_KEY`

## Frontend Environment Variables

Create a `.env.local` file in the `frontend/` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production (Vercel), set:
```env
NEXT_PUBLIC_API_URL=https://your-railway-backend-url.railway.app
```




