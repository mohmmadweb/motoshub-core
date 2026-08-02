# Motoshub frontend (Vite + React SPA) → built to static assets, served by nginx
# which also reverse-proxies the API/WS/static to the Django container.
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
# Same-origin by default: the browser calls /api/v1 and nginx proxies it.
ARG VITE_API_BASE=/api/v1
ARG VITE_WS_BASE=
ENV VITE_API_BASE=$VITE_API_BASE
ENV VITE_WS_BASE=$VITE_WS_BASE
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
