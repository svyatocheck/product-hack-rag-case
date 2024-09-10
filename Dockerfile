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
WORKDIR /app

# Команда для запуска приложения
CMD ["python", "-m", "http.server", "8000"]
