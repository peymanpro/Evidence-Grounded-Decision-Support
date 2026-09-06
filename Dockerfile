FROM python:3.12-slim AS builder

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
RUN pip install --no-cache-dir uv==0.7.22
COPY pyproject.toml README.md ./
COPY src ./src
RUN uv pip install --system --no-cache .

FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8000
RUN useradd --create-home --shell /usr/sbin/nologin app
COPY --from=builder /usr/local /usr/local
COPY --chown=app:app src ./src
USER app
EXPOSE 8000
CMD ["sh", "-c", "uvicorn wealthbrain.main:app --host 0.0.0.0 --port ${PORT}"]
