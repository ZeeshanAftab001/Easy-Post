# Frontend Dockerfile - Multi-stage
# Stage 1: Build static assets
FROM node:20-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine as production
# Copy build output to nginx folder
COPY --from=builder /app/dist /usr/share/nginx/html
# Copy custom nginx config for SPA routing (if any)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
