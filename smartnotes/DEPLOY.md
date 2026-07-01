# SmartNotes Deployment Guide

## Prerequisites

- Docker & Docker Compose
- Node.js 22+ (for local development)
- PostgreSQL 16 (provided via Docker)
- Redis 7 (provided via Docker)

## Environment Variables

Create a `.env` file in the root directory based on `.env.example`:

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `REDIS_URL` | ✅ | Redis connection string |
| `PORT` | ✅ | API port (default: 3000) |
| `NODE_ENV` | ✅ | `development` or `production` |
| `CORS_ORIGIN` | ✅ | Frontend URL for CORS |
| `AUTH0_DOMAIN` | ⚠️ | Required for production auth |
| `AUTH0_CLIENT_ID` | ⚠️ | Required for production auth |
| `AUTH0_CLIENT_SECRET` | ⚠️ | Required for production auth |
| `AUTH0_AUDIENCE` | ⚠️ | Required for production auth |
| `SENDGRID_API_KEY` | ❌ | Optional — enables email reminders |
| `SENDGRID_FROM_EMAIL` | ❌ | Email sender address |
| `SENTRY_DSN` | ❌ | Optional — enables error tracking |

## Local Development

```bash
# 1. Start database and Redis
docker compose up -d

# 2. Install dependencies
npm install

# 3. Generate Prisma client
npm run prisma:generate

# 4. Run database migrations
npm run prisma:migrate

# 5. Start the API (watches for changes)
npm run dev:api

# 6. In another terminal, start the web frontend
npm run dev:web
```

The API will be at `http://localhost:3000` and the web app at `http://localhost:5173`.

## Database Migrations

```bash
# Create a new migration
npm run prisma:migrate

# View the database in Prisma Studio
npm run prisma:studio

# Reset database (DESTRUCTIVE)
npx prisma migrate reset --schema=apps/api/prisma/schema.prisma
```

## Production Deployment

### Option 1: Docker Compose

```bash
# Build and start all services
docker compose -f docker-compose.prod.yml up -d --build

# Run migrations
docker compose -f docker-compose.prod.yml exec api \
  npx prisma migrate deploy --schema=prisma/schema.prisma

# Check health
curl http://localhost:3000/health
```

### Option 2: Railway

1. Create a new Railway project
2. Add a PostgreSQL service
3. Add a Redis service
4. Deploy the API:
   - Set the root directory to the project root
   - Set the Dockerfile path to `apps/api/Dockerfile`
   - Configure all environment variables listed above
5. Deploy the web app:
   - Set the Dockerfile path to `apps/web/Dockerfile`
   - Configure the `API_URL` environment variable to point to the API service
6. Run the initial migration:
   ```bash
   railway run npx prisma migrate deploy --schema=apps/api/prisma/schema.prisma
   ```

## Health Check

```bash
curl http://localhost:3000/health
# Expected: { "status": "ok", "timestamp": "...", "uptime": ... }
```

## Architecture

```
User → Web (React/Vite on nginx:80)
         ↓
       API (NestJS:3000) ← Reminder Worker (cron)
         ↓
       PostgreSQL + Redis
```

## Security Notes

- Never commit `.env` files with real secrets
- Auth0 is stubbed in development mode — **always set `NODE_ENV=production` in prod**
- Rate limiting is configured at 100 req/min per user
- CORS is restricted to the configured origin
