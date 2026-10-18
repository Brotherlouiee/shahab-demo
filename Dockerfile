# Syntax deliberately uses a small, reproducible Python runtime. Build context must be repository root.
FROM python:3.12-alpine@sha256:1b668429b3511ab407d8e00648891631b0b1a4d7e15e3ca70f38ab5b91ad4ab4 AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

ARG SOURCE_DATE_EPOCH
WORKDIR /app
RUN addgroup -g 10001 appuser && adduser -D -u 10001 -G appuser appuser
COPY requirements/image-build.lock requirements/image-runtime.lock ./requirements/
RUN python -m pip install --require-hashes --only-binary=:all: --no-compile -r requirements/image-build.lock \
    && python -m pip install --require-hashes --only-binary=:all: --no-compile -r requirements/image-runtime.lock
COPY pyproject.toml README.md ./
COPY backend ./backend
COPY alembic ./alembic
COPY alembic.ini ./
COPY data/contracts ./data/contracts
RUN python -m pip install --no-cache-dir --no-build-isolation --no-deps --no-compile . \
    && python -m pip check

USER appuser
EXPOSE 8000
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
