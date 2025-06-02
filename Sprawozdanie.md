Sprawozdanie - Zadanie 2
Temat
Opracowanie łańcucha CI/CD w usłudze GitHub Actions, który buduje obraz kontenera z aplikacji webowej (zadanie 1), skanuje go pod kątem podatności i publikuje do rejestru GHCR tylko wtedy, gdy obraz nie zawiera podatności o wysokim lub krytycznym poziomie zagrożenia.
Repozytorium: weather-app-lab1

Skład repozytorium
Repozytorium zawiera następujące pliki:

app.py — aplikacja webowa Flask umożliwiająca sprawdzenie pogody.
templates/index.html — szablon HTML dla formularza wyboru kraju i miasta.
requirements.txt — lista zależności aplikacji (Flask, requests, gunicorn).
Dockerfile — plik budujący wieloetapowy obraz kontenera oparty na Python 3.13.0-alpine.
.dockerignore — plik ignorujący niepotrzebne zasoby podczas budowania obrazu.
.github/workflows/build-and-push.yml — plik definicji CI/CD w GitHub Actions.


Etapy realizacji zadania
1. Budowa obrazu Docker (multiarch)
W pliku .github/workflows/build-and-push.yml zdefiniowano budowanie obrazu dla dwóch architektur: linux/amd64 i linux/arm64. Użyto akcji:

docker/setup-qemu-action@v3 do emulacji różnych architektur.
docker/setup-buildx-action@v3 do konfiguracji Buildx z platformami:
platforms: linux/amd64,linux/arm64


docker/build-push-action@v5 do budowy i pushowania obrazu.

2. Cache DockerHub
Zastosowano cache oparty o registry z trybem max, zapisując dane cache do publicznego repozytorium na DockerHub (dana123098/weather-app-cache:latest):
cache-from: type=registry,ref=${{ secrets.DOCKERHUB_USERNAME }}/weather-app-cache:latest
cache-to: type=registry,ref=${{ secrets.DOCKERHUB_USERNAME }}/weather-app-cache:latest,mode=max

Dzięki temu kolejne buildy wykorzystują warstwy z poprzednich kompilacji, co znacząco skraca czas budowy.

3. Publikacja do GHCR
Obraz jest publikowany do ghcr.io/dana123098/weather-app za pomocą akcji docker/build-push-action@v5. Publikacja następuje tylko wtedy, gdy obraz przejdzie test CVE. Logowanie do GHCR skonfigurowano za pomocą:
- name: Login to GitHub Container Registry
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GHCR_TOKEN }}

4. Test CVE (Trivy)
Do skanowania obrazu pod kątem podatności wykorzystano narzędzie Trivy za pomocą akcji aquasecurity/trivy-action@master. Początkowo skonfigurowano severity: CRITICAL, ale po analizie wymagań zadania zaktualizowano konfigurację na severity: CRITICAL,HIGH, aby blokować również wysokie zagrożenia:
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ghcr.io/dana123098/weather-app:latest
    format: table
    exit-code: '1'
    ignore-unfixed: true
    severity: CRITICAL,HIGH

Skaner przerywa pipeline przy wykryciu podatności o poziomie CRITICAL lub HIGH, blokując wysyłkę obrazu do GHCR.

Tagowanie obrazów i cache — opis i uzasadnienie
Tagowanie obrazów
W pliku build-and-push.yml użyto akcji docker/metadata-action@v5 do generowania tagów:
tags:
  type=raw,value=latest
  type=sha


latest — wskazuje na najnowszą wersję aplikacji, co ułatwia testy i wdrożenia w środowiskach deweloperskich.
sha — tag oparty na haślu commita (np. sha-f6e7b16), zapewnia unikalność i możliwość odtworzenia konkretnego stanu obrazu.

Uzasadnienie:

Tag sha umożliwia traceability i debugowanie, pozwalając odtworzyć obraz z konkretnej wersji kodu. Jest to zgodne z najlepszymi praktykami opisanymi w dokumentacji docker/metadata-action.
Użycie latest + sha to standard w CI/CD, stosowany m.in. przez GitHub, Docker i GitLab, co zapewnia elastyczność i kontrolę nad wersjonowaniem.

Tagowanie cache
Dane cache są zapisywane z tagiem weather-app-cache:latest:
ref=${{ secrets.DOCKERHUB_USERNAME }}/weather-app-cache:latest


Tag latest pozwala na ponowne wykorzystanie warstw dla wszystkich wersji aplikacji, co optymalizuje czas budowy.

Uzasadnienie:

Użycie latest dla cache maksymalizuje ponowne wykorzystanie warstw, co jest zalecane w dokumentacji docker/build-push-action. Publiczny cache na DockerHub dodatkowo spełnia wymaganie zadania i przyspiesza buildy, co jest kluczowe w środowiskach CI/CD.


Weryfikacja działania

Workflow GitHub Actions został uruchomiony wielokrotnie i zakończył się sukcesem
Obraz jest widoczny w GHCR: ghcr.io/dana123098/weather-app.
Dane cache są dostępne w publicznym repozytorium na DockerHub: dana123098/weather-app-cache:latest.
Lokalna aplikacja webowa działa poprawnie, co potwierdzają zrzuty ekranu (formularz wyboru kraju i miasta oraz integracja z API OpenWeatherMap).


Podsumowanie
Wszystkie wymagania zadania 2 zostały spełnione:

Zbudowano działający łańcuch CI/CD w GitHub Actions.
Obraz wspiera architektury linux/amd64 i linux/arm64.
Wykorzystano cache na DockerHub w trybie max.
Skanowanie CVE blokuje obrazy z podatnościami CRITICAL i HIGH.
Tagowanie zapewnia zarządzanie wersjami i traceability.

Repozytorium z kodem: https://github.com/Dana123098/weather-app-lab1
