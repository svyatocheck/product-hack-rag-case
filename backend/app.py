import streamlit as st
import random
from streamlit_cookies_manager import EncryptedCookieManager
import pandas as pd

# Инициализация менеджера cookies
cookies = EncryptedCookieManager(prefix="my_app/", password="your_secret_password")

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
    if "messages" not in cookies:
        cookies["messages"] = "[]"  # Присваиваем пустой список в виде строки

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
    messages = eval(cookies["messages"])  # Преобразуем строку в список
    for message in reversed(messages):  # Изменяем порядок на обратный
        st.write(message)

# Основная логика приложения
def chat_app():
    # Инициализация состояния для текстового поля
    if 'user_input' not in st.session_state:
        st.session_state.user_input = ""  # Инициализация состояния для текстового поля

    # Использование text_area с состоянием
    user_input = st.text_area("Введите ваше сообщение:", height=150, value=st.session_state.user_input)

    # Кнопка для очистки текстового поля
    if st.button("Очистить поле ввода"):
        st.session_state.user_input = ""  # Очищаем состояние, чтобы текстовое поле стало пустым

    # Обновляем значение текстового поля
    st.session_state.user_input = user_input

    if st.button("Отправить"):
        if user_input.strip():
            messages = eval(cookies["messages"])  # Преобразуем строку в список
            messages.append(f"Вы: {user_input}")
            cookies["messages"] = str(messages)  # Преобразуем список обратно в строку
            bot_reply = get_bot_response()
            messages.append(f"Бот: {bot_reply}")
            cookies["messages"] = str(messages)
            cookies.save()  # Сохраняем изменения в cookies
            st.success("Сообщение отправлено!")
            st.session_state.user_input = ""  # Очищаем поле ввода после отправки
        else:
            st.warning("Введите сообщение перед отправкой.")

    if st.button("Очистить чат"):
        cookies["messages"] = "[]"  # Присваиваем пустой список в виде строки
        cookies.save()  # Сохраняем изменения в cookies
        st.success("Чат очищен!")

    display_messages()

# Загрузка данных
def load_data():
    st.title("Загрузка данных")

    # Загрузка текстового документа
    text_file = st.file_uploader("Загрузите текстовый документ (txt, pdf)", type=["txt", "pdf"])
    if text_file is not None:
        st.write(f"Загружен файл: {text_file.name}")

    # Загрузка датасета
    dataset_file = st.file_uploader("Загрузите датасет (csv, xlsx)", type=["csv", "xlsx"])
    if dataset_file is not None:
        if dataset_file.type == "text/csv":
            data = pd.read_csv(dataset_file)
        else:
            data = pd.read_excel(dataset_file)
        st.write(f"Загружен датасет: {dataset_file.name}")
        st.dataframe(data)

# Основная функция
def main():
    st.sidebar.title("Меню")
    selected_tab = st.sidebar.radio("Выберите вкладку", ["Загрузка данных", "Чат", "Вкладка 3"])

    display_header()

    if selected_tab == "Чат":
        display_title()
        initialize_chat()
        chat_app()
    elif selected_tab == "Загрузка данных":
        load_data()
    elif selected_tab == "Вкладка 3":
        st.title("Вкладка 3")
        st.write("Здесь вы можете добавить функционал для третьей вкладки.")

# Запуск приложения
if __name__ == "__main__":
    main()