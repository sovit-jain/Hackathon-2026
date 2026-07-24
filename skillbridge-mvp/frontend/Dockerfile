# ---- Build stage ----
FROM node:20-alpine AS builder
WORKDIR /usr/src/app

# Bake NEXT_PUBLIC_API_URL at build time (required by Next.js)
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

RUN if [ -z "$NEXT_PUBLIC_API_URL" ]; then \
  echo "WARNING: NEXT_PUBLIC_API_URL not set at build time"; \
fi

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# ---- Runner stage ----
FROM node:20-alpine AS runner
WORKDIR /usr/src/app

ENV NODE_ENV=production

# standalone output includes its own minimal server.js
# it does NOT need the full node_modules from builder
COPY --from=builder /usr/src/app/public ./public
COPY --from=builder /usr/src/app/.next/standalone ./
COPY --from=builder /usr/src/app/.next/static ./.next/static

EXPOSE 3000

# Use PORT injected by Cloud Run (defaults to 8080 on Cloud Run)
# server.js from standalone respects the PORT env var natively
CMD ["node", "server.js"]
