FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends graphviz fontconfig curl \
    && rm -rf /var/lib/apt/lists/*
# IBM Plex Sans (licencia OFL) desde el repositorio oficial de IBM, la misma tipografía del deck
RUN mkdir -p /usr/share/fonts/truetype/plex && cd /usr/share/fonts/truetype/plex \
    && for w in Regular Medium SemiBold Bold; do \
         curl -fsSLO "https://raw.githubusercontent.com/IBM/plex/master/packages/plex-sans/fonts/complete/ttf/IBMPlexSans-$w.ttf"; \
       done \
    && fc-cache -f
RUN pip install --no-cache-dir matplotlib==3.9.2
RUN useradd --create-home --uid 10001 graficos
USER graficos
WORKDIR /datos
