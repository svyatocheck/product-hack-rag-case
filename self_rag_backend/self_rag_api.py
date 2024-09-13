import asyncio
from fastapi import FastAPI, HTTPException
from pydantic.v1 import BaseModel, Field
from typing import List, Dict
from self_rag_backend.self_rag_logic import *
from self_rag_backend.keys import *
import time
import jwt
import requests


filename = "npa_dataset_v3.db"  # change dataset version when new iteration begins!
database_path = f"/app/{filename}"

app = FastAPI()

# A simple in-memory store for Yandex GPT credentials
credentials_store = {
    "token": None,
    "folder_id": 'b1g5pkij4170jm1a1un6'
}

# Model for Yandex GPT credentials
class YandexGPTCredentials(BaseModel):
    token: str
    folder_id: str


def get_iam_token():
    with open("/app/jwt_token.txt", "r") as j:
        encoded_token = j.read()

    response = requests.post(
        "https://iam.api.cloud.yandex.net/iam/v1/tokens",
        headers={"Content-Type": "application/json"},
        json={"jwt": encoded_token},
    )

    return response.json()["iamToken"]


def yandex_logic():
    now = int(time.time())
    payload = {
        "aud": "https://iam.api.cloud.yandex.net/iam/v1/tokens",
        "iss": service_account_id,
        "iat": now,
        "exp": now + 3600,
    }

    # Формирование JWT.
    encoded_token = jwt.encode(
        payload, private_key, algorithm="PS256", headers={"kid": key_id}
    )

    # Запись ключа в файл
    with open("/app/jwt_token.txt", "w") as j:
        j.write(encoded_token)

    credentials_store["token"] = get_iam_token()


@app.get("/")
def read_root():
    return {"message": "FastAPI is running"}


async def rag_generate_answer(query: str) -> dict:
    try:
        yandex_logic()
        reflective_rag = SelfReflectiveRag(
            db_path = database_path, db_name = filename, gpt_folder_id = credentials_store["folder_id"], iam_token = credentials_store["token"]
        )
        questions = [query]
        value = reflective_rag.run_rag(questions)
        
        answer = value['generation']
        contexts = [texts.page_content for texts in value["documents"]]
        return {"answer":answer, "contexts":contexts}
    except Exception as ex:
        return {"answer":str(ex), "contexts":"None"}


# Endpoint 1: Handle RAG queries with timeout
@app.post("/rag/query", response_model=dict)
async def get_rag_answer(request: dict):
    try:
        response = await asyncio.wait_for(rag_generate_answer(request["query"]), timeout=180.0)
        return response
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="RAG system did not respond in time.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))