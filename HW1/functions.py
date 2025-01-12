import requests

# API_KEY = "da896315ea22ae56bf396661494f76de" # ВАШ ключ
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