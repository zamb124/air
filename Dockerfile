FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml ./
COPY uv.lock* ./

RUN if [ -f uv.lock ]; then uv sync --frozen; else uv sync; fi

COPY . .

RUN mkdir -p /app/data

EXPOSE 8001

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]

