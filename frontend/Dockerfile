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

FROM nginxinc/nginx-unprivileged:stable-alpine@sha256:782bb89768cc87b7f95c18b95baa1af250e5d451f26794f59363540161147c01 AS runtime
# Package installation needs root only while building; final USER remains 101:101.
USER 0
# Pin fixes for the base HIGH/MEDIUM findings; unavailable exact APKs fail the build.
RUN apk add --no-cache --upgrade musl=1.2.6-r3 musl-utils=1.2.6-r3 libexpat=2.9.0-r0 libx11=1.8.14-r0 zlib=1.3.2-r1 libxpm=3.5.20-r0
COPY frontend/nginx/nginx.conf /etc/nginx/nginx.conf
COPY frontend/nginx/api-disabled.conf /etc/nginx/shahab-api.conf
COPY --from=build /build/dist /srv/shahab
# No Node, npm, source files, API credential, or build-time secret in this stage.
USER 101:101
EXPOSE 8080
ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
