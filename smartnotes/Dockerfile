# Base Stage for installing dependencies and building
FROM node:20-alpine AS builder

WORKDIR /usr/src/app

# Copy package config
COPY package*.json ./
COPY tsconfig*.json ./
COPY nx.json ./

# Copy all project workspaces
COPY apps ./apps
COPY packages ./packages

# Install dependencies
RUN npm ci

# Generate Prisma Client
RUN npx prisma generate --schema=apps/api/prisma/schema.prisma

# Build the shared packages and the API
RUN npx nx build shared
RUN npx nx build api

# Production Stage
FROM node:20-alpine AS runner

WORKDIR /usr/src/app

# Copy built bundles and dependencies
COPY package*.json ./
RUN npm ci --omit=dev

# Copy generated Prisma Client, Schema, and Migration folder
COPY --from=builder /usr/src/app/node_modules/.prisma ./node_modules/.prisma
COPY --from=builder /usr/src/app/node_modules/@prisma/client ./node_modules/@prisma/client
COPY --from=builder /usr/src/app/apps/api/prisma ./apps/api/prisma
COPY --from=builder /usr/src/app/dist ./dist

# Create a folder for SQLite database persistent storage
RUN mkdir -p /data

EXPOSE 3000

ENV NODE_ENV=production
ENV PORT=3000
ENV DATABASE_URL="file:/data/smartnotes.db"

# Run Prisma migrations and start the backend
CMD npx prisma migrate deploy --schema=apps/api/prisma/schema.prisma && node dist/apps/api/main.js
