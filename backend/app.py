import streamlit as st
import random
from streamlit_cookies_manager import EncryptedCookieManager

# Инициализация менеджера cookies
# cookie_manager = EncryptedCookieManager(secret="your_secret_key")
cookies = EncryptedCookieManager(prefix="my_app/")
# cookie_manager.load()

if not cookies.ready():
    st.stop()  # Ждем, пока компонент загрузится

# Функция для отображения титульного текста
def display_header():
    st.markdown(
        """
        <h2 style='text-align: center;'>Кейс №9</h2>
        <p style='text-align: center; font-size: 30px;'>Экосистема знаний нормативных актов.</p>
        """,
        unsafe_allow_html=True
    )

# Заголовок приложения
def display_title():
    st.markdown("<h3 style='text-align: center;'>Введите ваш вопрос.</h3>", unsafe_allow_html=True)

# Инициализация состояния для хранения сообщений
def initialize_chat():
    if "messages" not in cookie_manager:
        cookie_manager["messages"] = []

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
    for message in cookie_manager["messages"]:
        st.write(message)

# Основная логика приложения
def chat_app():
    user_input = st.text_input("Введите ваше сообщение:")

    if st.button("Отправить"):
        if user_input.strip():
            # Добавляем сообщение пользователя
            cookie_manager["messages"].append(f"Вы: {user_input}")
            # Генерируем ответ бота
            bot_reply = get_bot_response()
            cookie_manager["messages"].append(f"Бот: {bot_reply}")
            cookie_manager.save()  # Сохраняем изменения в cookies
            st.success("Сообщение отправлено!")
        else:
            st.warning("Введите сообщение перед отправкой.")

    if st.button("Очистить чат"):
        cookie_manager["messages"] = []
        cookie_manager.save()  # Сохраняем изменения в cookies
        st.success("Чат очищен!")

    display_messages()

# Основная функция
def main():
    st.sidebar.title("Меню")
    selected_tab = st.sidebar.radio("Выберите вкладку", ["Чат", "Вкладка 2", "Вкладка 3"])

    display_header()

    if selected_tab == "Чат":
        display_title()
        initialize_chat()
        chat_app()
    elif selected_tab == "Вкладка 2":
        st.title("Вкладка 2")
        st.write("Здесь вы можете добавить функционал для второй вкладки.")
    elif selected_tab == "Вкладка 3":
        st.title("Вкладка 3")
        st.write("Здесь вы можете добавить функционал для третьей вкладки.")

# Запуск приложения
if __name__ == "__main__":
    main()