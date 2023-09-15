from fastapi.responses import JSONResponse
import torch
from pydantic import BaseModel
from typing import Dict
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from models.spot import inference
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pymongo import MongoClient
import os

app = FastAPI()

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB_NAME")]
collection = db[os.getenv("MONGO_COLLECTION_NAME")]
model_version = os.getenv("MODEL_VERSION")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Response(BaseModel):
    imr: Dict
    status: str


class HTTPErrorResponse(BaseModel):
    message: str
    status: str


class SentenceModel(BaseModel):
    sentence: str


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    response_model = HTTPErrorResponse(status="error", message=exc.detail)
    json_compatible_item_data = jsonable_encoder(response_model)
    return JSONResponse(
        status_code=exc.status_code,
        content=json_compatible_item_data,
    )


@app.post(
    "/transform-sentence-to-imr",
    response_model=Response,
    status_code=status.HTTP_200_OK,
)
@torch.inference_mode()
def transform_sentence_to_imr(body: SentenceModel):
    try:
        output = inference(body.sentence)
        if not output:
            raise HTTPException(
                status_code=status.HTTP_204_NO_CONTENT, detail="No output generated"
            )

        # Store data in MongoDB
        result_data = {
            "inputSentence": body.sentence,
            "imr": output["result"],
            "rawOutput": output["raw"],
            "status": "success",
            "modelVersion": model_version,
        }
        # Insert into MongoDB
        collection.insert_one(result_data.copy())

        result_data.pop("_id", None)

        return JSONResponse(content=result_data)
    except Exception as e:
        error_data = {
            "inputSentence": body.sentence if body else "N/A",
            "error": str(e),
            "status": "error",
            "modelVersion": model_version,
        }
        collection.insert_one(error_data)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
