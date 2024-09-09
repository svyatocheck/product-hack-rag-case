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
if st.button("Отправить"):
    if user_input:
        st.session_state.messages.append(user_input)
        st.success("Сообщение отправлено!")
        st.experimental_rerun()  # Перезагрузить приложение для обновления сообщений

# Отображение всех сообщений
display_messages()