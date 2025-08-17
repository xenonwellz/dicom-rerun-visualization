# Multi-stage build for Vite app with nginx
FROM oven/bun:1-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files from webviewer directory
COPY webviewer/package.json webviewer/bun.lock* ./

# Install dependencies
RUN bun install

# Copy webviewer source code
COPY webviewer/ .

# Build the application
RUN bun run build

# Production stage with nginx
FROM nginx:alpine

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

WORKDIR /usr/share/nginx/html

# Since i have built my rrd file and uploaded to a storage bucket, i can just download it and put it in the nginx folder
# Ideally, you will need to build this file in the dockerfile or in any build stage you prefer

RUN wget https://objects.xenrad.io/others/session.rrd -O session.rrd

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
