from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")

API_WEATHER_KEY = os.getenv("API_WEATHER_KEY")

URL_WEATHER = os.getenv("URL_WEATHER") # адрес запроса

# URL_NUTRITIONIX = "https://trackapi.nutritionix.com/v2/natural/nutrients"

APP_KEY_NUTRITIONIX = os.getenv("APP_KEY_NUTRITIONIX")

APP_ID_NUTRITIONIX = os.getenv("APP_ID_NUTRITIONIX")