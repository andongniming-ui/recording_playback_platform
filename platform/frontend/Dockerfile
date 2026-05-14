ARG NODE_BASE_IMAGE=node:18-bullseye-slim
FROM ${NODE_BASE_IMAGE}

WORKDIR /app

COPY package.json package-lock.json ./
ARG NPM_REGISTRY=
RUN set -eux; \
    if [ -n "$NPM_REGISTRY" ]; then npm config set registry "$NPM_REGISTRY"; fi; \
    for i in 1 2 3; do \
      npm ci --no-audit --no-fund && exit 0; \
      echo "npm ci attempt $i failed, retrying..."; \
      sleep 3; \
    done; \
    npm ci --no-audit --no-fund

COPY . .
ARG VITE_API_BASE_URL=
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
RUN npm run build

EXPOSE 5173

CMD ["sh", "-c", "printf 'window.__AREX_RECORDER_CONFIG__ = { VITE_API_BASE_URL: \"%s\" }\\n' \"${VITE_API_BASE_URL}\" > /app/dist/env.js && npm run preview -- --host 0.0.0.0 --port 5173"]
