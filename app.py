from flask import Flask, request, render_template
from datetime import datetime
import logging
import requests#Program używa biblioteki requests, aby wysłać żądanie HTTP do API OpenWeatherMap
import os
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
        return "Błąd: Brak klucza API WEATHER_API_KEY w zmiennych środowiskowych!"
    
    # Zapytanie do API OpenWeatherMap
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city},{country}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Sprawdzenie, czy żądanie się powiodło
        data = response.json()
        if data.get("main"):
            temp = data['main']['temp']
            weather_desc = data['weather'][0]['description']
            return f"Pogoda w {city}, {country}: {temp}°C, {weather_desc}"
        else:
            return "Błąd: Nie udało się pobrać pogody."
    except requests.RequestException as e:
        return f"Błąd: {str(e)}"
