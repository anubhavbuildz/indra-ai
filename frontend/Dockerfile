FROM node:22-bookworm-slim AS build
WORKDIR /frontend
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
# "/" resolves to the browser's current origin; Nginx forwards API requests.
ARG VITE_API_BASE_URL=/
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
RUN npm run build

FROM nginxinc/nginx-unprivileged:stable-alpine AS runtime
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /frontend/dist /usr/share/nginx/html
USER 101
EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=5s --retries=6 \
    CMD wget --quiet --spider http://127.0.0.1:8080/nginx-health || exit 1
