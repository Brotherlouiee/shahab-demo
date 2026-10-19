# Build tools stay outside the runtime. Both stages use the same pinned ABI.
FROM python:3.12-alpine@sha256:1b668429b3511ab407d8e00648891631b0b1a4d7e15e3ca70f38ab5b91ad4ab4 AS build
ARG SOURCE_DATE_EPOCH
ENV PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /build
COPY requirements/image-build.lock requirements/image-runtime.lock ./requirements/
RUN python -m pip install --require-hashes --only-binary=:all: --no-compile -r requirements/image-build.lock \
    && python -m venv --without-pip /opt/venv \
    && python -m pip --python /opt/venv/bin/python install --require-hashes --only-binary=:all: --no-compile -r requirements/image-runtime.lock
COPY pyproject.toml README.md ./
COPY backend ./backend
RUN python -m pip wheel --no-deps --no-build-isolation --wheel-dir /wheels . \
    && python -m pip --python /opt/venv/bin/python install --no-deps --no-index --no-compile /wheels/*.whl \
    && python -m pip --python /opt/venv/bin/python check \
    && /opt/venv/bin/python -c "import psycopg, sqlalchemy, uvloop, httptools"

FROM python:3.12-alpine@sha256:1b668429b3511ab407d8e00648891631b0b1a4d7e15e3ca70f38ab5b91ad4ab4 AS runtime
ARG SOURCE_DATE_EPOCH
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/opt/venv/bin:$PATH"
WORKDIR /app
# The base has its own pip, independently of our pip-free application venv.
# Runtime installs are unsupported; remove both installed and bundled installers.
RUN apk add --no-cache --upgrade zlib=1.3.2-r1 \
    && /usr/local/bin/python -m pip uninstall --yes pip \
    && rm -rf /usr/local/lib/python3.12/ensurepip \
    && /usr/local/bin/python -c "import importlib.util; assert importlib.util.find_spec('pip') is None; assert importlib.util.find_spec('ensurepip') is None" \
    && addgroup -g 10001 appuser && adduser -D -u 10001 -G appuser appuser
COPY --from=build /opt/venv /opt/venv
COPY pyproject.toml README.md ./
COPY backend ./backend
COPY alembic ./alembic
COPY alembic.ini ./
COPY data/contracts ./data/contracts
USER appuser
EXPOSE 8000
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
