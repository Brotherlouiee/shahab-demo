# Arvan VM deployment — agent brief

Operational notes for the production VM behind **Arvan CDN**. Use this when SSH-ing into the server or changing Compose/nginx. **Never paste `.env.prod` contents, Docker Hub tokens, or database passwords into chat or git.**

## SSH access

| Item | Value |
| --- | --- |
| Host | `85.198.52.5` |
| User | `root` (current Arvan setup) |
| Command | `ssh root@85.198.52.5` |

**Before changing the host:** UFW allows **22** (SSH) and **80** (HTTP origin) only. **fail2ban** protects SSH (5 failures / 10 minutes → 1 hour ban). Avoid repeated failed logins.

## Domain and URLs

| Item | Value |
| --- | --- |
| Primary hostname | `shahabfintech.ir` |
| `www` | Redirects to apex |
| Site | `https://shahabfintech.ir/` |
| API | Same origin: `https://shahabfintech.ir/api/v1/...` (no `api.` subdomain in this stack) |
| Liveness | `https://shahabfintech.ir/api/v1/health/live` |

**CDN:** Public TLS terminates at **Arvan**. Origin is **HTTP on port 80** on the VM. Browsers must use **HTTPS** at the edge so production **Secure** cookies (questionnaire proof) are stored and sent.

## Traffic path

```text
Browser ──HTTPS──► Arvan CDN
                      └── HTTP ──► Host nginx (:80)
                                        └── HTTPS ──► Docker frontend (127.0.0.1:8443)
                                                          ├── SPA static files
                                                          └── /api/v1/ ──► api:8000 (private Docker network)
```

- **Host nginx** is the public origin entrypoint (CDN → VM).
- **Frontend container nginx** serves static assets and proxies `/api/v1/` to the API. The API trusts **only** the frontend container’s fixed IP (`SHAHAB_FRONTEND_IP`, default `172.30.50.10`). **Do not** proxy from host nginx directly to `api:8000`.

## Paths on the server

| Path | Purpose |
| --- | --- |
| `/home/shahab/app/` | Deployment root |
| `/home/shahab/app/docker-compose.prod.yml` | Production Compose (pre-built images, no `build`) |
| `/home/shahab/app/.env.prod` | Private env (`chmod 600`) — read only on server |
| `/home/shahab/app/deploy/vm/nginx.conf.template` | In-container frontend nginx template (bind mount) |
| `/home/shahab/app/deploy/vm/api-grants.sql` | Runtime GRANTs for `shahab_api` role |
| `/home/shahab/tls/` | `fullchain.pem` + `privkey.pem` for **in-container** nginx (self-signed or replace with LE) |
| `/etc/nginx/sites-available/shahab` | **Host** nginx vhost |
| `/etc/nginx/sites-enabled/shahab` | Enabled symlink |

**Compose project name:** `shahab-prod` (e.g. volume `shahab-prod_postgres_data`).

**Pinned companion files from GitHub** (same revision as deployed stack when possible):

```text
release_ref=8e40f170b5313e49318af434b212f80cec5fefc8
https://raw.githubusercontent.com/Brotherlouiee/shahab-demo/$release_ref/
```

Files: `docker-compose.prod.yml`, `deploy/vm/nginx.conf.template`, `deploy/vm/api-grants.sql`, `.env.prod.example`.

## Docker commands

Always from `/home/shahab/app`:

```bash
cd /home/shahab/app

docker compose --env-file .env.prod -f docker-compose.prod.yml ps
docker compose --env-file .env.prod -f docker-compose.prod.yml logs --tail=100 api frontend
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --no-build --wait
```

**Private images:** `docker login --username shahab2026` (read token at password prompt only).

**Migrations (maintenance profile):**

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml --profile maintenance run --rm migrate
```

### `.env.prod` variables (names only)

- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` (migrator/owner)
- `SHAHAB_MIGRATION_DATABASE_URL` (migrator)
- `SHAHAB_DATABASE_URL` (non-owner login `shahab_api`)
- `SHAHAB_READINESS_TOKEN`
- `SHAHAB_PUBLIC_HOST=shahabfintech.ir`
- `SHAHAB_TLS_DIRECTORY=/home/shahab/tls`
- `SHAHAB_BIND_IP=127.0.0.1`
- `SHAHAB_HTTP_PORT=8080`, `SHAHAB_HTTPS_PORT=8443`
- `SHAHAB_APP_SUBNET`, `SHAHAB_FRONTEND_IP`
- Kavenegar / OTP vars (off until separately authorized)

URL-encode passwords in database URLs if they contain special characters.

## Host nginx (Arvan origin)

Config: `/etc/nginx/sites-available/shahab`.

Current behavior:

- Listens on **80** for `shahabfintech.ir` and `www.shahabfintech.ir`.
- If `X-Forwarded-Proto` is not `https`, respond **308** to `https://$host$request_uri` (forces browsers off plain HTTP for cookie/CSRF correctness).
- HTTPS visitors (CDN sets `X-Forwarded-Proto: https`): reverse-proxy to `https://127.0.0.1:8443` with `Host` and `X-Forwarded-Proto: https`.
- Rate limit on `/api/v1/`.

After edits:

```bash
nginx -t && systemctl reload nginx
```

**Docker port publish:** `127.0.0.1:8080→8080`, `127.0.0.1:8443→8443` only — not public host `:443`.

## In-container nginx (frontend service)

- Template mounted from `./deploy/vm/nginx.conf.template`; `envsubst` uses `SHAHAB_PUBLIC_HOST`.
- Includes `map $http_x_forwarded_proto $api_forwarded_proto` so the API sees the **client** scheme from the CDN chain (CSRF / cookie `Secure` alignment).
- After template changes:

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --no-build --force-recreate frontend
```

TLS files must be readable by container UID/GID **101** (see [vm-compose.md](vm-compose.md)).

## Security summary

- UFW: allow **22**, **80**; default deny inbound.
- fail2ban: `sshd` jail.
- Postgres, Redis, API not published on the public interface.
- Production: mock OTP disabled in Compose; catalogue import and live SMS are separate owner steps.

## Troubleshooting

| Symptom | Likely cause |
| --- | --- |
| POST `/questionnaire/sessions` **201** but PUT answers **403** “Questionnaire access is not allowed” | User on **http://** or missing **Secure** proof cookie — use **https://** and start a **new** session |
| **403** “Request origin is not allowed” | `Origin` vs API scheme mismatch — check `X-Forwarded-Proto` through host + container nginx |
| `frontend` unhealthy | TLS path/permissions under `SHAHAB_TLS_DIRECTORY` |
| `pull access denied` | Run `docker login` for `shahab2026` |

**On-server checks:**

```bash
curl -s -H 'Host: shahabfintech.ir' -H 'X-Forwarded-Proto: https' \
  http://127.0.0.1/api/v1/health/live

curl -sI http://shahabfintech.ir/ | head -5   # expect 308 to https
```

## Do not without explicit approval

- `docker compose down -v` (destroys DB volume)
- Publish API/Postgres/Redis on `0.0.0.0`
- Commit or share `.env.prod`
- Remove CDN/`X-Forwarded-Proto` nginx patches or bypass frontend when calling the API
- Force-push or production data changes outside approved runbooks

## Related repo docs

- [docker-compose.prod.yml](../../docker-compose.prod.yml)
- [.env.prod.example](../../.env.prod.example)
