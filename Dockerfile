FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml README.md .python-version ./
COPY app ./app
COPY main.py pytest.ini ./

RUN pip install --no-cache-dir uv && uv sync --frozen

CMD ["uv", "run", "python", "main.py"]
