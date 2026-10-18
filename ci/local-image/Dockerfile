FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/playwright-browsers
ENV PATH="/opt/ci-python/bin:/usr/local/bin:${PATH}"
ENV SHAHAB_E2E_BROWSER_PATH=/opt/chrome/chrome-linux64/chrome

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl git xz-utils \
    python3 python3-venv python3-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY node-v22.23.3-linux-x64.tar.xz /tmp/node.tar.xz

RUN echo "df450af89261115ef9f9e3830c3eeb2cc9213b63c720b1af623cb5dcbe2e02de  /tmp/node.tar.xz" | sha256sum -c - \
    && tar -xJf /tmp/node.tar.xz -C /usr/local --strip-components=1 \
    && rm /tmp/node.tar.xz \
    && python3 -m venv /opt/ci-python

COPY chrome-linux64.zip /tmp/chrome-linux64.zip

RUN apt-get update \
    && apt-get install -y --no-install-recommends unzip \
    && npm install --global playwright@1.63.0 \
    && playwright install-deps chromium \
    && unzip -t /tmp/chrome-linux64.zip \
    && mkdir -p /opt/chrome \
    && unzip -q /tmp/chrome-linux64.zip -d /opt/chrome \
    && chmod +x /opt/chrome/chrome-linux64/chrome \
    && rm /tmp/chrome-linux64.zip \
    && rm -rf /var/lib/apt/lists/*

RUN node --version \
    && python --version \
    && /opt/chrome/chrome-linux64/chrome --version

WORKDIR /workspace
