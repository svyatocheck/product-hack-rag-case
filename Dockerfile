# Указываем базовый образ
FROM python:3.10.11-slim

# Устанавливаем необходимые зависимости
RUN apt-get update && apt-get install -y \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем pip
RUN pip install --upgrade pip

# Устанавливаем некоторые часто используемые пакеты
RUN pip install numpy pandas matplotlib requests beautifulsoup4

# Устанавливаем директорию для работы
WORKDIR /app/backend

# Копируем файлы приложения
COPY . .

# Устанавливаем зависимости из requirements.txt
RUN pip install -r requirements.txt

# Экспонируем порт, на котором Streamlit слушает
EXPOSE 8501

# Запускаем Streamlit-приложение
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
