# ArrowTuner Frontend Dockerfile
FROM node:20-alpine AS builder

# Set work directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (including dev dependencies for build)
RUN npm install

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM node:20-alpine AS runner

# Set environment variables
ENV NODE_ENV=production
ENV PORT=3000

# Set work directory
WORKDIR /app

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nuxtjs -u 1001

# Copy built application from builder stage
COPY --from=builder --chown=nuxtjs:nodejs /app/.output /app/.output

# Set proper permissions
RUN chown -R nuxtjs:nodejs /app

# Switch to non-root user
USER nuxtjs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

# Expose port
EXPOSE 3000

# Run the application
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", ".output/server/index.mjs"]