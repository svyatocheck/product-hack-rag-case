import streamlit as st
import random


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
    st.title("Введите ваш вопрос.")

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
def chat_app():
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

# Основная функция
def main():
    # Боковая панель
    st.sidebar.title("Меню")
    
    # Вкладки
    tabs = ["Чат", "Вкладка 2", "Вкладка 3"]
    selected_tab = st.sidebar.radio("Выберите вкладку", tabs)


    # Отображение титульного текста
    display_header()
    
    # Отображение выбранной вкладки
    if selected_tab == "Чат":
        display_title()
        initialize_session_state()
        chat_app()
    elif selected_tab == "Вкладка 2":
        st.title("Вкладка 2")
        # Добавьте код для второй вкладки
    elif selected_tab == "Вкладка 3":
        st.title("Вкладка 3")
        # Добавьте код для третьей вкладки

# Запуск приложения
if __name__ == "__main__":
    main()