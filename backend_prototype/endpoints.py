from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

# Модель для запроса
class Question(BaseModel):
    question: str

# Эндпоинт для получения вопроса
@app.post("/ask")
async def ask_question(question: Question):
    # URL сервиса, куда будет отправлен вопрос
    service_url = "http://example.com/api/answer"  # Замените на реальный URL вашего сервиса

    try:
        # Отправляем вопрос в сервис
        response = requests.post(service_url, json={"question": question.question})
        response.raise_for_status()  # Проверка на ошибки HTTP

        # Получаем ответ от сервиса
        answer = response.json().get("answer", "Нет ответа.")
        return {"question": question.question, "answer": answer}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обращении к сервису: {str(e)}")

# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)