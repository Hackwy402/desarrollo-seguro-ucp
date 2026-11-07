FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends graphviz fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir pytm==1.3.1
RUN useradd --create-home --uid 10001 modelador
USER modelador
WORKDIR /modelo
