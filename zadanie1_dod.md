**Sprawozdanie**

**======== Z A D A N I E 1 ==========**

**\-\-\-\-\-\-- CZĘŚĆ OBOWIĄZKOWA \-\-\-\-\-\-\--**

**Opis aplikacji**

Aplikacja została napisana w języku Python z wykorzystaniem frameworka
Flask. Wykorzystuje API OpenWeatherMap do pobierania danych pogodowych
na podstawie wybranego kraju i miasta. Interfejs użytkownika (UI) składa
się z prostego formularza HTML, który pozwala na wybór kraju i miasta z
rozwijanych list, a po zatwierdzeniu wyświetla aktualną temperaturę i
opis pogody

**1. Plik app.py**

Plik app.py zawiera główną logikę aplikacji, w tym obsługę routingu,
logowanie i komunikację z API OpenWeatherMap.

*from* flask *import* Flask, request, render_template

*from* datetime *import* datetime

*import* logging

*import* requests

*import* os

*\# Inicjalizacja aplikacji Flask*

app = Flask(\_\_name\_\_)

*\# Konfiguracja logowania*

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(\_\_name\_\_)

*\# Logowanie wymaganych informacji przy uruchomieniu*

logger.info(f\"Data uruchomienia: {datetime.now()}\")

logger.info(\"Autor: Daiana Henina\")

logger.info(f\"Port TCP: {os.getenv(\'PORT\', \'5000\')}\")

*\# Predefiniowana lista krajów i miast*

countries_cities = {

    \"Poland\": \[\"Warsaw\", \"Krakow\"\],

    \"Germany\": \[\"Berlin\", \"Munich\"\]

}

\@app.route(\'/\')

def index():

    *\# Wyświetlenie formularza z wyborem kraju i miasta*

    *return* render_template(\'index.html\', countries=countries_cities)

\@app.route(\'/weather\', methods=\[\'POST\'\])

def weather():

    *\# Pobranie danych z formularza*

    country = request.form\[\'country\'\]

    city = request.form\[\'city\'\]

   

    *\# Pobranie klucza API z zmiennej środowiskowej*

    api_key = os.getenv(\"WEATHER_API_KEY\")

    *if* not api_key:

        *return* \"Błąd: Brak klucza API WEATHER_API_KEY w zmiennych
środowiskowych!\"

   

    *\# Zapytanie do API OpenWeatherMap*

    url =
f\"http://api.openweathermap.org/data/2.5/weather?q={city},{country}&appid={api_key}&units=metric\"

    *try*:

        response = requests.get(url)

        response.raise_for_status()  *\# Sprawdzenie, czy żądanie się
powiodło*

        data = response.json()

        *if* data.get(\"main\"):

            temp = data\[\'main\'\]\[\'temp\'\]

            weather_desc = data\[\'weather\'\]\[0\]\[\'description\'\]

            *return* f\"Pogoda w {city}, {country}: {temp}°C,
{weather_desc}\"

        *else*:

            *return* \"Błąd: Nie udało się pobrać pogody.\"

    *except* requests.RequestException *as* e:

        *return* f\"Błąd: {str(e)}\"

**Plik templates/index.html**

Plik index.html definiuje formularz HTML, który pozwala użytkownikowi
wybrać kraj i miasto.

\<!DOCTYPE *html*\>

\<html *lang*=\"pl\"\>

\<head\>

    \<meta *charset*=\"UTF-8\"\>

    \<title\>Sprawdź pogodę\</title\>

\</head\>

\<body\>

    \<h1\>Sprawdź pogodę\</h1\>

    \<form *action*=\"/weather\" *method*=\"POST\"\>

        \<label *for*=\"country\"\>Wybierz kraj:\</label\>

        \<select *name*=\"country\" *id*=\"country\" *required*\>

            {% for country in countries %}

                \<option *value*=\"{{ country }}\"\>{{ country
}}\</option\>

            {% endfor %}

        \</select\>

        \<br\>\<br\>

        \<label *for*=\"city\"\>Wybierz miasto:\</label\>

        \<select *name*=\"city\" *id*=\"city\" *required*\>

            {% for country, cities in countries.items() %}

                {% for city in cities %}

                    \<option *value*=\"{{ city }}\"\>{{ city
}}\</option\>

                {% endfor %}

            {% endfor %}

        \</select\>

        \<br\>\<br\>

        \<button *type*=\"submit\"\>Sprawdź pogodę\</button\>

    \</form\>

\</body\>

\</html\>

**3. Plik requirements.txt**

Plik requirements.txt zawiera listę zależności wymaganych przez
aplikację.

flask

requests

gunicorn

Plik definiuje biblioteki Pythona używane w aplikacji:

- flask: Framework do budowy aplikacji webowej.

- requests: Biblioteka do wysyłania żądań HTTP do API OpenWeatherMap.

- gunicorn: Serwer WSGI do uruchamiania aplikacji w kontenerze.

**Plik Dockerfile:**

*\# Argument określający platformę budowania (dla wieloplatformowości)*

ARG BUILDPLATFORM

*\# Etap 1: Budowa - instalacja zależności*

FROM \--platform=\$BUILDPLATFORM python:3.13.0-alpine AS builder

WORKDIR /app

*\# Kopiowanie pliku z zależnościami jako pierwsza warstwa dla lepszego
wykorzystania cache*

COPY requirements.txt .

*\# Instalacja pip i zależności w katalogu użytkownika*

RUN pip install \--no-cache-dir \--upgrade pip && pip install
\--no-cache-dir \--user -r requirements.txt

*\# Etap 2: Obraz końcowy - minimalizacja rozmiaru*

FROM python:3.13.0-alpine

WORKDIR /app

*\# Kopiowanie zależności z etapu builder*

COPY \--from=builder /root/.local /root/.local

*\# Kopiowanie plików aplikacji*

COPY app.py .

COPY templates/ templates/

*\# Ustawienie zmiennych środowiskowych*

ENV
PATH=/root/.local/bin:/usr/local/bin:/usr/local/sbin:/usr/sbin:/sbin:/bin

ENV PORT=5000

*\# Metadane zgodne ze standardem OCI - informacje o autorze*

LABEL org.opencontainers.image.author=\"Daiana Henina
\<danaqwer5@gmail.com\>\"

*\# Eksponowanie portu, na którym aplikacja nasłuchuje*

EXPOSE 5000

*\# Komenda uruchamiająca aplikację za pomocą Gunicorn*

CMD \[\"gunicorn\", \"\--bind\", \"0.0.0.0:5000\", \"app:app\"\]

**Plik .dockerignore**

Plik .dockerignore został użyty do zoptymalizowania kontekstu budowy
poprzez wykluczenie niepotrzebnych plików i katalogów.

\_\_pycache\_\_

\*.pyc

.venv

pyvenv.cfg

\*.md

screenshots/

.git

.gitignore

a\. Budowa obrazu:

![](media/image1.png){width="4.25767716535433in"
height="3.1209831583552057in"}

b\. Uruchomienie kontenera:

![](media/image2.png){width="6.3in" height="0.54375in"}

**c. Logi:**

![Obraz zawierający tekst, zrzut ekranu, Czcionka Zawartość wygenerowana
przez sztuczną inteligencję może być
niepoprawna.](media/image3.png){width="6.3in"
height="1.4854166666666666in"}

d\. Analiza obrazu:

**Sprawdzenie rozmiaru obrazu Docker:**

![](media/image4.png){width="6.3in" height="0.6638888888888889in"}

**Polecenie analizy warstw:**

![Obraz zawierający tekst, menu, zrzut ekranu, Czcionka Zawartość
wygenerowana przez sztuczną inteligencję może być
niepoprawna.](media/image5.png){width="4.064074803149606in"
height="4.229379921259842in"}

**Formularz w przeglądarce:**

![Obraz zawierający tekst, zrzut ekranu, Czcionka, oprogramowanie
Zawartość wygenerowana przez sztuczną inteligencję może być
niepoprawna.](media/image6.png){width="3.1469520997375326in"
height="2.3306583552055993in"}

**Pobieranie pogody:**

![Obraz zawierający tekst, zrzut ekranu, Czcionka, linia Zawartość
wygenerowana przez sztuczną inteligencję może być
niepoprawna.](media/image7.png){width="3.7679483814523183in"
height="1.2625251531058617in"}

**\-\-\-\-\-\-- CZĘŚĆ NIEOBOWIĄZKOWA (DODATKOWA) \-\-\-\-\-\-\-\-\-\--**

**2. (max. +50%)**

![](media/image8.png){width="6.3in" height="2.1666666666666665in"}

Aktywacja buildera:

![](media/image9.png){width="4.845299650043745in"
height="4.443661417322835in"}

![](media/image10.png){width="4.91090113735783in"
height="0.8764052930883639in"}

**Budowa obrazu z cache'em:**

![](media/image11.png){width="6.3in" height="6.3284722222222225in"}

![Obraz zawierający tekst, zrzut ekranu, Czcionka Zawartość wygenerowana
przez sztuczną inteligencję może być
niepoprawna.](media/image12.png){width="6.3in"
height="2.495138888888889in"}

**Potwierdzenie manifestu:**

![Obraz zawierający tekst, zrzut ekranu, Czcionka Zawartość wygenerowana
przez sztuczną inteligencję może być
niepoprawna.](media/image13.png){width="6.3in"
height="6.341666666666667in"}

**Analiza podatności na zagrożenia**

![Obraz zawierający tekst, zrzut ekranu, Czcionka, menu Zawartość
wygenerowana przez sztuczną inteligencję może być
niepoprawna.](media/image14.png){width="6.3in"
height="3.6791666666666667in"}

**Przesłanie obrazu do Docker Hub**

Polecenie logowania:

![Obraz zawierający tekst, zrzut ekranu, Czcionka Zawartość wygenerowana
przez sztuczną inteligencję może być
niepoprawna.](media/image15.png){width="6.3in"
height="1.4583333333333333in"}

**Wnioski**

W ramach realizacji zadań obowiązkowych opracowano aplikację pogodową
(zadanie 1), która poprawnie integruje się z API OpenWeatherMap,
prezentując dane pogodowe dla wybranych lokalizacji. Plik Dockerfile
(zadanie 2) został zaprojektowany z wykorzystaniem wieloetapowego
budowania, optymalizacji cache'u i minimalizacji warstw, co pozwoliło
uzyskać obraz o rozmiarze 89.6 MB. Proces budowy został zoptymalizowany
dzięki plikowi .dockerignore, który wykluczył niepotrzebne pliki, a
uruchomienie kontenera (zadanie 3) potwierdziło poprawność działania
aplikacji, co zweryfikowano logami i testem w przeglądarce

W części nieobowiązkowej (zadanie 2 dodatkowe) zbudowano obraz
wieloplatformowy (linux/amd64 i linux/arm64) zgodny ze standardem OCI,
wykorzystując buildera docker-container i dane cache z eksporterem
registry oraz backend-em inline. Proces budowy został przyspieszony
dzięki cache'owi, a manifest potwierdził wsparcie dla obu platform.
Obraz został pomyślnie przesłany do repozytorium danagen/weather-app na
Docker Hub.
