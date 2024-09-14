import logging
from logging.handlers import RotatingFileHandler

# Настройка уровня логирования
LOG_LEVEL = logging.INFO

# Создание регистратора
logger = logging.getLogger('my_app')
logger.setLevel(LOG_LEVEL)

# Создание обработчика для записи в файл
file_handler = RotatingFileHandler('app.log', maxBytes=1024*1024*100, backupCount=20)
file_handler.setLevel(logging.DEBUG)

# Создание обработчика для вывода в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)

# Создание форматировщика
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Применение форматировщика к обработчикам
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Добавление обработчиков к регистратору
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Функция для логирования
def log_message(level, message):
    logger.log(level, message)

# Пример использования
if __name__ == '__main__':
    log_message(logging.INFO, "This is an info message")
    log_message(logging.WARNING, "This is a warning message")
    log_message(logging.ERROR, "This is an error message")
