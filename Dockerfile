FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_FILE_WATCHER_TYPE=none

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy the uv executable from its official image.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install third-party dependencies first so Docker can cache this layer.
COPY pyproject.toml uv.lock ./

RUN uv sync \
    --frozen \
    --no-dev \
    --no-install-project

# Copy README.md, main.py, app/, and the rest of the project.
COPY . .

# Install the local rag-project1 package now that app/ exists.
RUN uv sync \
    --frozen \
    --no-dev

EXPOSE 8501

CMD [
    "uv",
    "run",
    "--no-sync",
    "streamlit",
    "run",
    "main.py"
]