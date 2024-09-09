import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Заголовок страницы
st.title("Простой чат-бот")

# Функция main()
def main():
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
        
        # Обновляем HTML-структуру чата
        html_chat = """
        <div id="chat-container">
            <div class="message-user">{}</div>
            <div class="message-bot">{}</div>
        </div>
        """.format(user_message, bot_response_message)
        
        # Обновляем состояние Streamlit
        st.markdown(html_chat, unsafe_allow_html=True)

    # Пример таблицы данных
    data = {
        'Имя': ['Николай', 'Сергей', 'Игорь'],
        'Возраст': [29, 13, 40]
    }
    df = pd.DataFrame(data)
    st.write("Пример таблицы данных:")
    st.dataframe(df)

    # Отображение истории чата
    for message in reversed(chat_history):
        html_chat = """
        <div id="chat-container">
            <div class="message-user">{}</div>
            <div class="message-bot">{}</div>
        </div>
        """.format(message["content"])
        st.markdown(html_chat, unsafe_allow_html=True)

    # Стили CSS для чата
    css = """
    <style>
    .message-user {
        background-color: #e6f3ff;
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 20px 20px 0 20px;
    }
    .message-bot {
        background-color: #dcf8c6;
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 0 20px 20px 0;
    }
    #chat-container {
        width: 80%;
        margin: auto;
        text-align: center;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
