import streamlit as st
import random

# Заголовок приложения
st.title("Простой чат на Streamlit")

# Состояние для хранения сообщений
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Предопределенные ответы бота
bot_responses = [
    "Привет! Как я могу помочь?",
    "Интересно, расскажите больше!",
    "Я здесь, чтобы помочь вам!",
    "Какой у вас вопрос?",
    "Спасибо за ваше сообщение!",
]

# Функция для отображения сообщений
def display_messages():
    for message in st.session_state.messages:
        st.write(message)

# Поле ввода для сообщения
user_input = st.text_input("Введите ваше сообщение:")

# Обработка отправки сообщения
if st.button("Отправить", key="send_button"):
    if user_input:
        # Добавляем сообщение пользователя
        st.session_state.messages.append(f"Вы: {user_input}")
        
        # Генерируем ответ бота
        bot_reply = random.choice(bot_responses)
        st.session_state.messages.append(f"Бот: {bot_reply}")
        
        st.success("Сообщение отправлено!")
        user_input = ""  # Очистить поле ввода

# Отображение всех сообщений
display_messages()