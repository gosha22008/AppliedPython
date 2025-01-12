import requests
import asyncio
import aiohttp


URL="https://api.openweathermap.org/data/2.5/weather" # адрес запроса

def get_current_temp(city_name, API_KEY):
    '''
    Функция делает запрос к апи, полученный ответ содержит
    текущую температуру в укзанном городе.
    Параметры:
        city_name - название города для которого хотим узнать температуру
        appid - ключ
        units - metric  -- указание единиц измерения (Цельсий)
    '''

    params={
        "q": city_name,
        "appid": API_KEY,
        'units': 'metric'
    }

    response = requests.get(url=URL, params=params)
    return response

current_season = "winter"

def is_normal(city_name, current_temp, df):
    '''
    Функция сравниет текущую температуру с порогами верхним и нижним,
    и на основе этого возвращает либо True - температура нормальная,
    либо False - температура аномальная
    Параметры:
        city_name - название города
        current_temp - текущая температура
    '''
    limit_up = df[(df["city"] == city_name) & (df["season"] == current_season)]["temp_up_limit"].iloc[0] # верхний порог
    limit_down = df[(df["city"] == city_name) & (df["season"] == current_season)]["temp_down_limit"].iloc[0] # нижний порог
    return (current_temp < limit_up) or (current_temp > limit_down) #возвращает True если температура нормальная