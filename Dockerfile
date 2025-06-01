# Argument określający platformę budowania (dla wieloplatformowości)
ARG BUILDPLATFORM

# Etap 1: Budowa - instalacja zależności
FROM --platform=$BUILDPLATFORM python:3.13.0a6-alpine3.20 AS builder
WORKDIR /app

# Kopiowanie pliku z zależnościami jako pierwsza warstwa dla lepszego wykorzystania cache
COPY requirements.txt .

# Zaktualizuj system i doinstaluj wymagane biblioteki z konkretnymi wersjami
RUN apk update && \
    apk upgrade --no-cache && \
    apk add --no-cache \
      openssl=3.3.3-r0 \
      sqlite-libs=3.45.3-r2 \
      xz-libs=5.6.2-r1 && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt

# Etap 2: Obraz końcowy - minimalizacja rozmiaru
FROM python:3.13.0a6-alpine3.20
WORKDIR /app

# Skopiuj wymagane biblioteki z etapu builder
COPY --from=builder /root/.local /root/.local

# Skopiuj kod aplikacji
COPY app.py .
COPY templates/ templates/

# Utwórz użytkownika nie-root
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# Ustawienia środowiskowe
ENV PATH=/root/.local/bin:$PATH
ENV PORT=5000

# Dodaj metadane OCI
LABEL org.opencontainers.image.author="Daiana Henina <danaqwer5@gmail.com>"

# Udostępnienie portu
EXPOSE 5000

# Komenda uruchamiająca aplikację
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
