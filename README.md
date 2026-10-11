# Shahab financing demo

Original React/Vite prototype with supplied CSS, logos, and local icons.

## Run

Use Node.js 22.12 or newer.

```sh
npm ci
npm run dev
```

For local FastAPI setup, environment configuration, and health checks, see the
[backend bootstrap guide](docs/operations/fastapi-local-bootstrap.md).

## Build and host

```sh
npm run build
```

Publish the `dist` directory on a static host. Build command: `npm run build`.

SMS login and financing recommendations are demo flows, not live services. Some home-page photos and fonts use external URLs.

The original additional icon sheet is preserved in `design/icons.zip`; the app uses the individual SVG icons supplied in `assets`.

## Manual API testing — US-09.T081

[Swagger/Postman instructions](docs/api/manual-testing.md) and [restricted environment runbook](docs/runbook/api-testing.md) describe the generated API contract and real test flow. An approved HTTPS API/PostgreSQL host is still required; the online testing task is not complete from artifacts or CI alone.

