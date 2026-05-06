ARG PYTHON_BASE_IMAGE=python:3.11-slim
FROM ${PYTHON_BASE_IMAGE}
WORKDIR /app
COPY requirements.txt /tmp/requirements.txt
ARG PIP_INDEX_URL=
ARG PIP_EXTRA_INDEX_URL=
ARG PIP_TRUSTED_HOST=
RUN set -eux; \
    pip_args="--no-cache-dir --default-timeout=120 --retries=5"; \
    if [ -n "$PIP_INDEX_URL" ]; then pip_args="$pip_args --index-url $PIP_INDEX_URL"; fi; \
    if [ -n "$PIP_EXTRA_INDEX_URL" ]; then pip_args="$pip_args --extra-index-url $PIP_EXTRA_INDEX_URL"; fi; \
    if [ -n "$PIP_TRUSTED_HOST" ]; then pip_args="$pip_args --trusted-host $PIP_TRUSTED_HOST"; fi; \
    pip install $pip_args -r /tmp/requirements.txt
COPY backend/ /app/
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
