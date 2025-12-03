# LinkedIn Prospection Agent

A full-stack application for automating LinkedIn connection requests and follow-up messages with AI-generated personalized content.

## Features

- **CSV Import**: Upload CSV files with LinkedIn profiles
- **Automated Connections**: Send connection requests with personalized messages
- **AI Message Generation**: Uses Mistral AI to generate personalized connection and follow-up messages
- **Follow-up Automation**: Automatically sends follow-up messages after a configured delay
- **Dashboard**: View statistics and monitor connection status
- **Message History**: Track all messages sent to profiles
- **Profile Management**: View and filter imported profiles

## Architecture

- **Backend**: Python FastAPI on Railway
- **Frontend**: Next.js (TypeScript/React) on Vercel
- **Database**: PostgreSQL (Railway managed)
- **Automation**: Playwright for browser automation
- **AI**: Mistral AI API for message generation

## Setup

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install chromium
```

5. Create a `.env` file:
```bash
cp .env.example .env
```

6. Update `.env` with your configuration:
```
DATABASE_URL=postgresql://user:password@localhost:5432/linkedin_agent
MISTRAL_API_KEY=your-mistral-api-key
LINKEDIN_EMAIL=your-email@example.com
LINKEDIN_PASSWORD=your-password
RATE_LIMIT_DELAY=45
FOLLOWUP_DAYS=7
SECRET_KEY=your-secret-key-change-in-production
```

7. Run database migrations:
```bash
alembic upgrade head
```

8. Start the server:
```bash
uvicorn app.main:app --reload
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env.local` file:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Start the development server:
```bash
npm run dev
```

## Deployment

### Railway (Backend)

1. Create a new Railway project
2. Add a PostgreSQL database
3. Connect your GitHub repository
4. Set environment variables in Railway dashboard
5. Deploy

The `railway.json` file is already configured for deployment.

### Vercel (Frontend)

1. Create a new Vercel project
2. Connect your GitHub repository
3. Set environment variables:
   - `NEXT_PUBLIC_API_URL`: Your Railway backend URL
4. Deploy

## CSV Format

The CSV file should contain at least a LinkedIn URL column. The system will automatically detect columns with names like:
- `url`, `linkedin`, `profile` → LinkedIn URL
- `name`, `full name` → Profile name
- `company`, `organization` → Company name
- `title`, `position`, `role` → Job title
- `notes`, `comment` → Additional notes
- `tags` → Tags (comma-separated)

Example CSV:
```csv
name,linkedin_url,company,title
John Doe,https://www.linkedin.com/in/johndoe,Acme Corp,Software Engineer
Jane Smith,https://www.linkedin.com/in/janesmith,Tech Inc,Product Manager
```

## Important Notes

⚠️ **LinkedIn Terms of Service**: This tool automates LinkedIn interactions. Please ensure you comply with LinkedIn's Terms of Service. Automated actions may result in account restrictions.

- Use rate limiting appropriately
- Be respectful of other users
- Don't send spam messages
- Monitor your account for any restrictions

## License

MIT

