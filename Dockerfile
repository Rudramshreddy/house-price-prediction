ARG PYTHON_VERSION=3.13

FROM python:${PYTHON_VERSION}-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install uv

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

COPY . .

RUN adduser -m appuser

USER appuser

CMD ["uv", "run", "uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]