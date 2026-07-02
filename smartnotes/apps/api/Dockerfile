# ============================================
# SmartNotes API — Build and Run
# ============================================

# Stage 1: Build
FROM node:22-alpine AS builder
WORKDIR /app

# Copy all files for build
COPY . .

# Install all dependencies
RUN npm install

# Build the workspace
RUN cd packages/shared && npm run build
RUN npx prisma generate --schema=apps/api/prisma/schema.prisma
RUN cd apps/api && npm run build

# Prune dev dependencies for the final image
RUN npm prune --production

# Stage 2: Production Runner
FROM node:22-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

# Copy built artifacts and production node_modules
COPY --from=builder /app/apps/api/dist ./dist
COPY --from=builder /app/apps/api/prisma ./prisma
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/apps/api/package.json ./package.json

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:3000/health || exit 1

CMD ["node", "dist/main"]
