import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Заголовок страницы
st.title("Простой чат-бот")

# Сайдбар
st.sidebar.header("Параметры")
user_name = st.sidebar.text_input("Введите ваше имя:")
age = st.sidebar.slider("Выберите ваш возраст", 0, 100, 25)

# Основная область
st.write(f"Привет, {user_name}!")
st.write(f"Ваш возраст: {age}")

# Заглушка для ответа бота
def bot_response(user_message):
    # Здесь будет реализован алгоритм ответа бота
    # Для сейчас мы возвращаем простую фразу
    return "Я понимаю вас. Что еще я могу сделать для вас?"

# Чат-бот
chat_history = []
user_message = st.text_area("Введите сообщение для бота:", height=100)
if user_message:
    chat_history.append({"role": "user", "content": user_message})
    bot_response_message = bot_response(user_message)
    chat_history.append({"role": "bot", "content": bot_response_message})
    st.chat(chat_history[-2], theme="light")  # Отображаем последнее сообщение пользователя
    st.chat(chat_history[-1], theme="dark")  # Отображаем последний ответ бота

# Пример таблицы данных (оставляем как есть)
data = {
    'Имя': ['Николай', 'Сергей', 'Игорь'],
    'Возраст': [29, 13, 40]
}
df = pd.DataFrame(data)
st.write("Пример таблицы данных:")
st.dataframe(df)

# Отображение истории чата
for message in reversed(chat_history):
    st.chat(message, theme="dark" if message["role"] == "user" else "light")