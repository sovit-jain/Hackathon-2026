# Build stage: install dependencies and build the Next.js app
FROM node:20-alpine AS builder
WORKDIR /usr/src/app

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
CMD ["npm", "start", "--", "-p", "3000"]
