import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from rag import *
import time
import jwt
import requests


filename = "npa_dataset_v3.db"  # change dataset version when new iteration begins!
database_path = f"/home/jupyter/datasphere/s3/hack-object-storage/database/{filename}"
dataset_path = (
    "/home/jupyter/datasphere/datasets/npa_two/preprocessed_dataset_ver_2.txt"
)

app = FastAPI()

# A simple in-memory store for Yandex GPT credentials
credentials_store = {
    "token": None,
    "folder_id": 'b1g5pkij4170jm1a1un6'
}

# Base models for RAG input and output
class RAGRequest(BaseModel):
    query: str


class RAGResponse(BaseModel):
    answer: str
    contexts: List[Dict[str, str]]


# Model for Yandex GPT credentials
class YandexGPTCredentials(BaseModel):
    token: str
    folder_id: str


def get_iam_token(service_account_id, private_key, key_id):
    now = int(time.time())
    payload = {
        "aud": "https://iam.api.cloud.yandex.net/iam/v1/tokens",
        "iss": service_account_id,
        "iat": now,
        "exp": now + 3600,
    }
    encoded_token = jwt.encode(
        payload, private_key, algorithm="PS256", headers={"kid": key_id}
    )

    response = requests.post(
        "https://iam.api.cloud.yandex.net/iam/v1/tokens",
        headers={"Content-Type": "application/json"},
        json={"jwt": encoded_token},
    )

    return response.json()["iamToken"]


def yandex_logic():
    # set keys here
    service_account_id = "ajelb1fgokcofo2dgcq2"
    key_id = "ajeinv58ca4aeosoqncn"
    private_key = """
    PLEASE DO NOT REMOVE THIS LINE! Yandex.Cloud SA Key ID <ajeinv58ca4aeosoqncn>
    -----BEGIN PRIVATE KEY-----
    MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDdMSrElRTJ99DW
    M0p0jeI55UgagNvuuj56CbBKvBLc8TFlBy82Awarg5p28Cyp3sYBaHFFOHSm73+j
    WwK5m6WXTYy0Az83Vz+Km07ONUifCgf6WmMgoErBtjfSTPQirWnyq19veiLul7xg
    7Tf14gcLqfEosZmIZOD/gxxGgCxb+2NFKJFCKvUFc9Z3hweksuacwtafqmhYNVtF
    adlPIzwhZ7G7+bPzDW16VjyG5CMlPksZms7S/7X/rc+EtGgnT2z2EnwqbEWsoT8w
    AERHLkvGPMjxF8nSvQ8mf1lNIIOrDHrJrV9/DRyKfs3d6HO0Pa0WT1PrrwBlwpnV
    bVhsMHSZAgMBAAECggEASZjIcCxihGkOdZcPWQS0lyrw+NCTXTVfAGAk5lj5tcYS
    91iSntgW6g6Z4KU9VzAmleVYev2z4q+huorXt0ZQrK1C+cpyyEkhfU77w6T7Ct/d
    k7FrdjmfZiDpJfIw8TDeJb5bvM3YvaaDKYUEr62LRpg/A5lESpu2OY44ZETVfazj
    AU8M6VMzQ7mqjkjuGIMpuF9lyys0H8ju8/6le2hVdbe9wP9p9iWg9J+9iB0w1Ke0
    rWaboQpwRMOAw3fX4WBwBZkF5hgLxsADnYsuVaSdUPFLnISKiv+kYG1GTSqx+2zo
    9puey38F6nRDuDtFfJO3S6+qFFLwaQxIaPpJw7unWQKBgQDlx2B4keMqAlbx2nXn
    KuG2M1iN6/iXT8qmNXK8GNNMTxExUj39oSYt0mBpC7NwBwgQZrIOhFdm2uCsLQDt
    m4uA7OsLj2kFBv2WaOgH0XuVAdWQCyoy5fQ9Mw2Kt3geH0h+TdenIiwETH6u/7wt
    /vCUIv9sP4KQtENwZWNRkY1upwKBgQD2bvEW7FckUYA7j0pRsi1kNq+MIRM+D7Tl
    C0wp/Amgz8O2Vl9I1sG3DDv1Vzv1eUKWZdthDc42r+vy9nzZUco+wS0gvNkDkRjR
    r0beUdVV2Q7oh3GUlRXXU7c6Zgdz6gbCGF4fBtn8uuMk/YG98y4DAP1UUEkGqyAl
    RFXJjFCqvwKBgQC0y5GejLt+3GRo3AmVIGqEoBX3ZUouVHwRF1D1q1rmWfgfJKTe
    IaQWvcdaH/jKFt5DeWp0fbD/nwzUrHxkeNTlVoUCjY6GhB+X72dSb4OblNvjAMXt
    Un5AgSEQmpeKq/awWrNqMDsODtpG+7WnQ0csZ/UtyTMEhLHjiAMDtVDhVQKBgAJD
    fp9xSFOjFAR4Cny5oEUdY3tsCls1lbnM4sQ39natseSI4pMutdTSnfJg/MICfSQY
    h21azRwffZFbxkXQxITTDXERiwTHXmz+qS39nnINbl+gbuCohezWbgZxTXw5GBrM
    UoECdRonNVLvqTNvemq4pZsSqbkP9VmiSQ9y5ILNAoGBAKuFhBcSU66uvrJIYgrs
    TO3q4+lbIE4D3kFsZ40OGtttIqfKF8GCXzxNSrU1cSZmMX0V+nA6sCHh+UF/rYMw
    hQ1XjhP3+szls8AKvQa0rKKnDHWwdjv0FXxeD8jZBVY8ekQbg7ECHQLkGWuUnhpM
    SeHk81fwBqye8o0CyyKoFsph
    -----END PRIVATE KEY-----
    """
    # Получаем IAM-токен
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
    with open("jwt_token.txt", "w") as j:
        j.write(encoded_token)

    # Получаем IAM-токен
    credentials_store["token"] = get_iam_token()


@app.get("/")
def read_root():
    return {"message": "FastAPI is running"}


# Mock function for RAG answer generation
async def rag_generate_answer(query: str) -> RAGResponse:
    reflective_rag = SelfReflectiveRag(
        db_path = database_path, db_name = filename, gpt_folder_id = credentials_store["folder_id"], iam_token = credentials_store["token"]
    )
    questions = [query]
    value = reflective_rag.run_rag(questions)
    
    answer = value['generation']
    contexts = "</sp>\n\n".join([texts.page_content for texts in value["documents"]])
    
    return RAGResponse(answer=answer, contexts=contexts)


# Endpoint 1: Handle RAG queries with timeout
@app.post("/rag/query", response_model=RAGResponse)
async def get_rag_answer(request: RAGRequest):
    try:
        # Set a timeout of 5 seconds for the RAG generation process
        response = await asyncio.wait_for(rag_generate_answer(request.query), timeout=180.0)
        return response
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="RAG system did not respond in time.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint 2: Setup Yandex GPT credentials
@app.post("/yandex/gpt")
def setup_yandex_gpt():
    try:
        yandex_logic()
        return {"message": "Yandex GPT credentials set successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Optional: Endpoint to verify Yandex GPT credentials
@app.get("/yandex/gpt/verify")
def verify_yandex_gpt():
    if credentials_store["token"] and credentials_store["folder_id"]:
        return {
            "token": credentials_store["token"],
            "folder_id": credentials_store["folder_id"]
        }
    else:
        raise HTTPException(status_code=400, detail="Yandex GPT credentials not set.")

