from pydantic import BaseModel
from typing import Dict
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from pymongo import MongoClient
from tf_inference import generate
from yaml_parser import validate_and_fix_yaml
from adopt_generation import adopt_generation
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
def transform_sentence_to_imr(body: SentenceModel):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        raw_output = generate(body.sentence)
        parsed_result = validate_and_fix_yaml(raw_output)
        output = adopt_generation(parsed_result)
        if not output:
            raise HTTPException(
                status_code=status.HTTP_204_NO_CONTENT, detail="No output generated"
            )

        raw_output = output['result']
        imr_result = adopt_generation(raw_output)

        # Store data in MongoDB
        result_data = {
            "timestamp": timestamp,
            "inputSentence": body.sentence,
            "imr": imr_result,
            "rawOutput": raw_output,
            "status": "success",
            "modelVersion": model_version,
            "prompt": None
        }

        # Insert into MongoDB
        collection.insert_one(result_data.copy())

        result_data.pop("_id", None)

        return JSONResponse(content=result_data)
    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_data = {
            "timestamp": timestamp,
            "inputSentence": body.sentence if body else "N/A",
            "rawOutput": raw_output,
            "error": str(e),
            "status": "error",
            "modelVersion": model_version,
            "prompt": None
        }
        collection.insert_one(error_data)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )