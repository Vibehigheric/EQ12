FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Create non-root user for security
RUN addgroup -g 1001 -S eq12 && \
    adduser -S eq12 -u 1001

# Change ownership of app directory
RUN chown -R eq12:eq12 /app

# Switch to non-root user
USER eq12

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/probot || exit 1

# Start the application
CMD ["npm", "start"]
