import streamlit as st
import pandas as pd
from dotenv import load_dotenv

st.title("Пример приложения")

# Хранение контекста



st.sidebar.header("Параметры")
user_name = st.sidebar.text_input("Введите ваше имя:")
age = st.sidebar.slider("Выберите ваш возраст", 0, 100, 25)


st.write(f"Привет, {user_name}!")
st.write(f"Ваш возраст: {age}")

data = {
    'Имя': ['Николай', 'Сергей', 'Игорь'],
    'Возраст': [29, 13, 40]
}
df = pd.DataFrame(data)
st.write("Пример таблицы данных:")
st.dataframe(df)
