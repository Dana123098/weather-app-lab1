# Argument określający platformę budowania (dla wieloplatformowości)
ARG BUILDPLATFORM

# Etap 1: Budowa - instalacja zależności
FROM --platform=$BUILDPLATFORM python:3.13.0-alpine AS builder
WORKDIR /app

# Kopiowanie pliku z zależnościami jako pierwsza warstwa dla lepszego wykorzystania cache
COPY requirements.txt .
# Instalacja pip i zależności w katalogu użytkownika
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt

# Etap 2: Obraz końcowy - minimalizacja rozmiaru
FROM python:3.13.0-alpine
WORKDIR /app

# Kopiowanie zależności z etapu builder
COPY --from=builder /root/.local /root/.local

# Kopiowanie plików aplikacji
COPY app.py .
COPY templates/ templates/

# Ustawienie użytkownika nie-root dla bezpieczeństwa
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# Ustawienie zmiennych środowiskowych
ENV PATH=/root/.local/bin:/usr/local/bin:/usr/local/sbin:/usr/sbin:/sbin:/bin
ENV PORT=5000
# WEATHER_API_KEY będzie przekazywane w runtime przez GitHub Actions

# Metadane zgodne ze standardem OCI - informacje o autorze
LABEL org.opencontainers.image.author="Daiana Henina <danaqwer5@gmail.com>"

# Eksponowanie portu, na którym aplikacja nasłuchuje
EXPOSE 5000

# Komenda uruchamiająca aplikację za pomocą Gunicorn z 4 workerami
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]