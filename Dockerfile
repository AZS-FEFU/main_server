FROM python:3.12-alpine

WORKDIR /backend

# README.md needed to hatchling build
COPY pyproject.toml requirements.lock README.md .
RUN	pip install uv --no-cache
RUN	uv pip install --no-cache --system -r requirements.lock

COPY . .

CMD ["granian", "--interface", "asgi", "src/app.py", "--log", "--host", "0.0.0.0", "--port", "8000"]
# granian --interface asgi src/app.py --log --host 0.0.0.0 --port 8000
