FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN apt-get update && apt-get install -y --no-install-recommends pipx
# RUN pipx install uv
ENV PATH="/root/.local/bin:${PATH}"
RUN pipx install uv
RUN uv sync

COPY . .

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]