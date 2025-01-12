import streamlit as st
import pandas as pd
from functions import get_current_temp
import requests



st.header("Приветствую в моём streamlit приложении! Начнём!")

uploaded_file = st.file_uploader(label="Загрузите файл с историческими данными формата csv")
if uploaded_file:

    try:

        df = pd.read_csv(uploaded_file)
        st.success(body="Файл загружен успешно")
        st.dataframe(df.head(5))

        cities = df["city"].unique().tolist()
        city = st.selectbox(label="Выберите город", options=cities)

    except Exception as e:
        st.error(f"Что-то не так в загрузке данных: {e}")

    st.write(f"Описательные статистики для {city} за всё время")
    st.dataframe(df[df["city"] == city]["temperature"].describe().T)

    st.write(f"Описательные статистики для {city} по сезонам")
    st.dataframe(df[df["city"] == city].groupby(["season"]).describe())

    st.write(f"Сезонные профили с указанием среднего и стандартного отклонения")
    st.dataframe(df[df["city"] == city].groupby(["season"])["temperature"].agg(["mean", "std"]))

    API_KEY = st.text_input("Введите ключ API")
    if API_KEY:
        try:
            response = get_current_temp(city, API_KEY)

            if response.json()["cod"] == 401:
                st.error('{"cod":401, "message": "Invalid API key. Please see https://openweathermap.org/faq#error401 for more info."}')

            elif response.json()["cod"] == 200: 
                st.success(body="Ключ получен")
                current_temp = response.json()["main"]["temp"]
                st.write(f"Текущая температура в {city} -- {current_temp}")

        except Exception as e:
            st.error(f"Что-то не так с API: {e}")
    else:
        pass