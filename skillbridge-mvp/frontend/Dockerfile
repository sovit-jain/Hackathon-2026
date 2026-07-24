# Build stage: install dependencies and build the Next.js app
FROM node:20-alpine AS builder
WORKDIR /usr/src/app

# Next.js requires NEXT_PUBLIC_API_URL at build time
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

# If NEXT_PUBLIC_API_URL is not provided, print a warning (will need to be passed at build time)
RUN if [ -z "$NEXT_PUBLIC_API_URL" ]; then echo "WARNING: NEXT_PUBLIC_API_URL not set at build time. Must pass --build-arg NEXT_PUBLIC_API_URL=<backend-url> to docker build"; fi

# Install exact dependencies from package-lock.json
COPY package.json package-lock.json ./
RUN npm ci

# Copy source files and build the production app
COPY . .
RUN npm run build

# Run stage: use production-only files and node_modules
FROM node:20-alpine AS runner
WORKDIR /usr/src/app
ENV NODE_ENV=production

# Copy package metadata and built output from the builder stage
COPY --from=builder /usr/src/app/package.json ./
COPY --from=builder /usr/src/app/node_modules ./node_modules
COPY --from=builder /usr/src/app/.next ./.next
COPY --from=builder /usr/src/app/public ./public
COPY --from=builder /usr/src/app/next.config.js ./next.config.js

# Expose the port that Cloud Run routes to
EXPOSE 3000

# Start the Next.js app in production on port 3000
CMD ["sh", "-c", "npm start -- -p $PORT"]
