from flask import Flask, request, render_template
from datetime import datetime
import logging
import requests  # Program używa biblioteki requests, aby wysłać żądanie HTTP do API OpenWeatherMap
import os

# Wyłączenie logów werkzeug (poza błędami)
logging.getLogger('werkzeug').setLevel(logging.ERROR)

# Inicjalizacja aplikacji Flask
app = Flask(__name__)

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Logowanie wymaganych informacji przy uruchomieniu
logger.info(f"Data uruchomienia: {datetime.now()}")
logger.info("Autor: Daiana Henina")
logger.info(f"Port TCP: {os.getenv('PORT', '5000')}")

# Predefiniowana lista krajów i miast
countries_cities = {
    "Poland": ["Warsaw", "Krakow"],
    "Germany": ["Berlin", "Munich"]
}

@app.route('/')
def index():
    # Wyświetlenie formularza z wyborem kraju i miasta
    return render_template('index.html', countries=countries_cities)

@app.route('/weather', methods=['POST'])
def weather():
    # Pobranie danych z formularza
    country = request.form['country']
    city = request.form['city']
    
    # Pobranie klucza API z zmiennej środowiskowej
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        logger.error("Brak klucza API WEATHER_API_KEY w zmiennych środowiskowych")
        return "Błąd: Brak klucza API WEATHER_API_KEY w zmiennych środowiskowych!"

    # Zapytanie do API OpenWeatherMap
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city},{country}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Sprawdzenie, czy żądanie się powiodło
        data = response.json()
        logger.info(f"Odpowiedz API dla {city}, {country}: {data}")
        if data.get("main"):
            temp = data['main']['temp']
            weather_desc = data['weather'][0]['description']
            return f"<h2>Pogoda w {city}, {country}</h2><p>Temperatura: {temp}°C, Opis: {weather_desc}</p><a href='/'>Powrót</a>"
        else:
            logger.warning(f"Nie udało się pobrać pogody dla {city}, {country}")
            return "Błąd: Nie udało się pobrać pogody."
    except requests.RequestException as e:
        logger.error(f"Błąd API OpenWeatherMap: {str(e)}")
        return f"Błąd: {str(e)}"

# Uruchomienie aplikacji Flask
if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host="0.0.0.0", port=port, debug=True)