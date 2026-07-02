# ============================================
# SmartNotes Web — Build and Serve
# ============================================

# Stage 1: Build
FROM node:22-alpine AS builder
WORKDIR /app

# Copy all files for build
COPY . .

# Install all dependencies (including dev)
RUN npm install

# Build the workspace
RUN cd packages/shared && npm run build
RUN cd apps/web && npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine AS runner

COPY --from=builder /app/apps/web/dist /usr/share/nginx/html

# Nginx config for SPA routing
RUN echo 'server { \
  listen 80; \
  location / { \
    root /usr/share/nginx/html; \
    try_files $uri $uri/ /index.html; \
  } \
  location /api { \
    proxy_pass http://smartnotes-api:3000; \
    proxy_http_version 1.1; \
    proxy_set_header Upgrade $http_upgrade; \
    proxy_set_header Connection "upgrade"; \
    proxy_set_header Host $host; \
  } \
  location /health { \
    proxy_pass http://smartnotes-api:3000; \
  } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:80 || exit 1
