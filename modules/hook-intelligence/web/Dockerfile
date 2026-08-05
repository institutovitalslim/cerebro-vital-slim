# syntax=docker/dockerfile:1.7
FROM node:22.14.0-alpine3.21 AS dependencies
WORKDIR /app
COPY web/package.json web/package-lock.json ./
RUN npm ci

FROM node:22.14.0-alpine3.21 AS builder
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1 \
    HOOK_API_URL=http://backend:8000
COPY --from=dependencies /app/node_modules ./node_modules
COPY web/ ./
RUN npm run build

FROM node:22.14.0-alpine3.21 AS runtime
WORKDIR /app
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    HOSTNAME=0.0.0.0 \
    PORT=3000 \
    HOOK_API_URL=http://backend:8000

COPY --from=builder --chown=node:node /app/.next/standalone ./
COPY --from=builder --chown=node:node /app/.next/static ./.next/static

USER node
EXPOSE 3000
CMD ["node", "server.js"]
