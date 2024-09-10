import streamlit as st
import random

# Заголовок приложения
def display_title():
    st.title("Простой чат на Streamlit")

# Инициализация состояния для хранения сообщений
def initialize_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []

# Предопределенные ответы бота
def get_bot_response():
    bot_responses = [
        "Привет! Как я могу помочь?",
        "Интересно, расскажите больше!",
        "Я здесь, чтобы помочь вам!",
        "Какой у вас вопрос?",
        "Спасибо за ваше сообщение!",
        "С удовольствием отвечу на ваши вопросы!",
        "Это звучит интересно!",
        "Могу предложить несколько идей.",
        "Какой у вас любимый фильм?",
        "Давайте обсудим это подробнее.",
        "Как вы себя чувствуете сегодня?",
        "Есть ли что-то, что вас беспокоит?",
        "Я всегда рад помочь!",
        "Какой ваш любимый вид спорта?",
        "Что нового в вашей жизни?",
        "Какой у вас план на сегодня?",
        "Если у вас есть вопросы, не стесняйтесь задавать!",
    ]
    return random.choice(bot_responses)

# Отображение всех сообщений
def display_messages():
    for message in st.session_state.messages:
        st.write(message)

# Основная логика приложения
def main():
    display_title()
    initialize_session_state()

    # Поле ввода для сообщения
    user_input = st.text_input("Введите ваше сообщение:")

    # Обработка отправки сообщения
    if st.button("Отправить", key="send_button"):
        if user_input:
            # Добавляем сообщение пользователя
            st.session_state.messages.append(f"Вы: {user_input}")
            
            # Генерируем ответ бота
            bot_reply = get_bot_response()
            st.session_state.messages.append(f"Бот: {bot_reply}")
            
            st.success("Сообщение отправлено!")
            user_input = ""  # Очистить поле ввода

    # Отображение всех сообщений
    display_messages()

# Запуск приложения
if __name__ == "__main__":
    main()