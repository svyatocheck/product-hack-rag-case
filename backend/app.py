import streamlit as st

# Заголовок приложения
st.title("Простой чат на Streamlit")

# Состояние для хранения сообщений
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Функция для отображения сообщений
def display_messages():
    for message in st.session_state.messages:
        st.write(message)

# Поле ввода для сообщения
user_input = st.text_input("Введите ваше сообщение:")

# Обработка отправки сообщения
if st.button("Отправить", key="send_button"):
    if user_input:
        st.session_state.messages.append(user_input)
        st.success("Сообщение отправлено!")
        user_input = ""  # Очистить поле ввода

# Отображение всех сообщений
display_messages()