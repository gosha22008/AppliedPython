import asyncio
import aiohttp
from config import API_WEATHER_KEY, URL_WEATHER, APP_ID_NUTRITIONIX, APP_KEY_NUTRITIONIX
from googletrans import Translator
import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# загрузка температуры через API 
async def async_get_temp(session, city):
    params={
        "q": city,
        "appid": API_WEATHER_KEY,
        'units': 'metric'
    }
    async with session.get(URL_WEATHER, params=params) as response:
        temp = await response.json()
        # print(temp["main"]["temp"], f" -- {city}")
        return temp["main"]["temp"]

async def main_temp(city):
    async with aiohttp.ClientSession() as session:
        resp = await asyncio.gather(async_get_temp(session, city))
        return resp[0]

# подсчёт нормы калорий
async def get_calorie_cal(PROFILE_DATA):
    '''
    Калории=10×Вес (кг)+6.25×Рост (см)−5×Возраст
    + Уровень активности добавляет калории (200-400 в зависимости от времени и типа тренировки).
    Можете указать формулу на свой выбор
    '''
    if not PROFILE_DATA.get("calorie_goal"):
        dop_calories = 400 if int(PROFILE_DATA.get("activity")) >= 60 else 200
        norm_calories = 10 * int(PROFILE_DATA.get("weight")) + 6.25 * int(PROFILE_DATA.get("height")) - 5 * int(PROFILE_DATA.get("age")) + dop_calories
        PROFILE_DATA["calorie_goal"] = norm_calories
        return norm_calories
    else:
        return PROFILE_DATA["calorie_goal"]

# подсчет нормы воды
async def get_water_cal(PROFILE_DATA):
    '''
    Базовая норма=Вес×30мл/кг 
    +500мл  за каждые 30 минут активности.
    +500−1000мл  за жаркую погоду (> 25°C).
    '''
    if not PROFILE_DATA.get("water_goal"):
        temp = int(PROFILE_DATA.get("current_temp"))
        if temp:
            dop_water_activ = 500 * int(PROFILE_DATA.get("activity"))//30
            dop_water_temp = 750 if temp > 25 else 0
            norm_water = int(PROFILE_DATA.get("weight")) * 30 + dop_water_temp + dop_water_activ
            PROFILE_DATA["water_goal"] = norm_water
            return norm_water
        else:
            print("Темп не задана")
    else:
        return PROFILE_DATA["water_goal"]
    

#функция переводчик через googletrans
async def translate_text(product:str):
    async with Translator() as translator:
        result = await translator.translate(product, dest='en', src='ru')
        return result.text

# функиця обращения к API Nutritionix
async def get_calories_info(query, path):

    URL_NUTRITIONIX = "https://trackapi.nutritionix.com/v2/natural/" + path

    headers = {
    'x-app-id': APP_ID_NUTRITIONIX,
    'x-app-key': APP_KEY_NUTRITIONIX,
    'Content-Type': 'application/json'
    }

    data = {
        "query": query,
        # "timezone": "US/Eastern"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url=URL_NUTRITIONIX, headers=headers, data=json.dumps(data)) as response:
            if response.status == 200:
                    logging.info(f"response.status = 200")
                    resp = await response.json()
                    if path == "nutrients":
                        logging.info(f"ЗАПРОС ЕДА")
                        return resp["foods"][0]["nf_calories"]
                    elif path == "exercise":
                        logging.info(f"ЗАПРОС УПРАЖНЕНИЯ")
                        return resp["exercises"][0]["nf_calories"]
            else:
                print(f"Ошибка API: {response.status}, {await response.text()}")

