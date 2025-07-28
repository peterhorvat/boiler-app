# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM node:20-alpine AS production

WORKDIR /app

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nuxt -u 1001

# Copy built application
COPY --from=builder --chown=nuxt:nodejs /app/.nuxt /app/.nuxt
COPY --from=builder --chown=nuxt:nodejs /app/.output /app/.output
COPY --from=builder --chown=nuxt:nodejs /app/node_modules /app/node_modules
COPY --from=builder --chown=nuxt:nodejs /app/package*.json /app/

# Switch to non-root user
USER nuxt

# Expose port
EXPOSE 3000

# Set environment
ENV NUXT_HOST=0.0.0.0
ENV NUXT_PORT=3000

# Start the application
CMD ["npm", "run", "preview"]