# syntax=docker/dockerfile:1
FROM python:3.12-slim AS build
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/pip pip install poetry==2.4.3
COPY pyproject.toml poetry.lock ./
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
RUN --mount=type=cache,target=/root/.cache/pypoetry poetry install --only main --no-root

FROM python:3.12-slim AS runtime
LABEL org.opencontainers.image.source="https://github.com/Stenishh/C216---L1"
WORKDIR /app
RUN groupadd --gid 1001 app && useradd --uid 1001 --gid app app
COPY --from=build --chown=1001:1001 /app/.venv /app/.venv
COPY --chown=1001:1001 src ./src
COPY --chown=1001:1001 alembic ./alembic
COPY --chown=1001:1001 alembic.ini ./
ENV PATH="/app/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
USER 1001:1001
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
