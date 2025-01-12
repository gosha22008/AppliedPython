import streamlit as st
import pandas as pd
from functions import get_current_temp, is_normal
import asyncio
import matplotlib.pyplot as plt
import seaborn as sbn


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

    # подготовка датасета для удобства
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["av_temp_season_city"] = df.groupby(["city", "season"])["temperature"].transform(lambda x: x.mean())
    df["std_season_city"] = df.groupby(["season", "city"])["temperature"].transform(lambda x: x.std())
    df["temp_up_limit"] = df["av_temp_season_city"] + 2 * df["std_season_city"]
    df["temp_down_limit"] = df["av_temp_season_city"] - 2 * df["std_season_city"]
    df["is_anomale"] = (df["temperature"] > df["temp_up_limit"] ) | (df["temperature"] < df["temp_down_limit"])

    # Временной ряд температур с выделением аномалий (например, точками другого цвета).
    plt.figure(figsize=(17,10))
    sbn.lineplot(x=df[df["city"] == "London"]["timestamp"],
                 y=df[df["city"] == "London"]["temperature"],
                 label="Тумпература", color="green")
    sbn.scatterplot(x=df[(df["city"] == "London") & (df["is_anomale"] == True)]["timestamp"],
                    y=df[(df["city"] == "London") & (df["is_anomale"] == True)]["temperature"],
                    label="Аномалии", color="red")
    plt.title(f"Температура в {city}")
    st.pyplot(plt)

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

                norm = is_normal(city_name=city, current_temp=current_temp, df=df)
                if norm:
                    st.success(body="Погода в пределах нормы")
                else:
                    st.warning(body="Внимание! Аномальная температура")

        except Exception as e:
            st.error(f"Что-то не так с API: {e}")
    else:
        pass