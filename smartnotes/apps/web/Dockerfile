# ============================================
# SmartNotes Web — Build and Serve
# ============================================

# Stage 1: Build
FROM node:22-alpine AS builder
WORKDIR /app

# Accept API URL as a build argument
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

# Copy all files for build
COPY . .

# Install all dependencies
RUN npm install

# Build the workspace
RUN cd packages/shared && npm run build
RUN cd apps/web && npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine AS runner

COPY --from=builder /app/apps/web/dist /usr/share/nginx/html

# Nginx config for SPA routing - using variable for proxy_pass to avoid crash if host is not yet resolvable
RUN echo 'server { \
  listen 80; \
  location / { \
    root /usr/share/nginx/html; \
    try_files $uri $uri/ /index.html; \
  } \
  location /api { \
    resolver 127.0.0.11 valid=30s; \
    set $api_service smartnotes-api; \
    proxy_pass http://$api_service:3000; \
    proxy_http_version 1.1; \
    proxy_set_header Upgrade $http_upgrade; \
    proxy_set_header Connection "upgrade"; \
    proxy_set_header Host $host; \
  } \
  location /health { \
    resolver 127.0.0.11 valid=30s; \
    set $api_service smartnotes-api; \
    proxy_pass http://$api_service:3000; \
  } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:80 || exit 1
