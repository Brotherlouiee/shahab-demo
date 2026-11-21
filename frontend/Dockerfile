# Build from the repository root: docker build -f frontend/Dockerfile .
# Base indexes are pinned; dependency resolution uses the existing npm lockfile.
FROM node:22-alpine@sha256:0a7108bf6c7bf5de370ffb1a3ed6be93d405b43ff159f681a8d18c0e2bc2e402 AS build
WORKDIR /build
COPY package.json package-lock.json ./
RUN npm ci
COPY index.html vite.config.js ./
COPY scripts/vite-dev-config.mjs ./scripts/vite-dev-config.mjs
COPY src ./src
COPY assets ./assets
COPY public ./public
COPY data/contracts ./data/contracts
RUN npm run build

FROM nginx/nginx-unprivileged:1.30.7-alpine3.24@sha256:0c53a1f2890c3526bfd201440f0fd3970e5b78f80630f58284aad0d34b5ec7bd AS runtime
# Package installation needs root only while building; final USER remains 101:101.
USER 0
# Pin base fixes; keep CA certificates explicit and remove curl, which runtime and health checks do not use.
RUN apk add --no-cache --upgrade ca-certificates-bundle=20260909-r0 libxslt=1.1.43-r4 musl=1.2.6-r3 musl-utils=1.2.6-r3 libexpat=2.10.0-r0 libx11=1.8.14-r0 zlib=1.4-r0 libxpm=3.5.20-r0 brotli-libs=1.2.1-r0 libxml2=2.13.9-r3 \
    && apk del curl libcurl
COPY frontend/nginx/nginx.conf /etc/nginx/nginx.conf
COPY frontend/nginx/api-disabled.conf /etc/nginx/shahab-api.conf
COPY --from=build /build/dist /srv/shahab
# No Node, npm, source files, API credential, or build-time secret in this stage.
USER 101:101
EXPOSE 8080
ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
