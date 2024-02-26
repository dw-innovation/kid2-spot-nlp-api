import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Optional

from adopt_generation import adopt_generation, AdoptFuncError
from tf_inference import generate, ModelException
from yaml_parser import validate_and_fix_yaml, ParseError

app = FastAPI()

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
    inputSentence: str
    status: str
    rawOutput: object
    status: str
    modelVersion: str
    error: Optional[str]
    prompt: Optional[str]


class HTTPErrorResponse(BaseModel):
    message: str
    status: str


class SentenceModel(BaseModel):
    sentence: str


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    response_model = HTTPErrorResponse(status="error", message=str(exc.detail))
    json_compatible_item_data = jsonable_encoder(response_model)
    return JSONResponse(
        status_code=400,
        content=json_compatible_item_data,
    )


@app.post(
    "/transform-sentence-to-imr",
    response_model=Response,
    status_code=status.HTTP_200_OK,
)
def transform_sentence_to_imr(body: SentenceModel):
    imr_result = None
    raw_output = None
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        raw_output = generate(body.sentence)
        parsed_result = validate_and_fix_yaml(raw_output)
        imr_result = adopt_generation(parsed_result)
    except (ModelException, ParseError, AdoptFuncError) as error:
        print("Exception is caught!!")
        error_data = {
            "timestamp": timestamp,
            "inputSentence": body.sentence,
            "imr": imr_result,
            "rawOutput": raw_output,
            "status": "error",
            "error": str(error),
            "modelVersion": model_version,
            "prompt": None
        }
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error_data
        )

    result_data = {
        "timestamp": timestamp,
        "inputSentence": body.sentence,
        "imr": imr_result,
        "rawOutput": raw_output,
        "status": "success",
        "modelVersion": model_version,
        "prompt": None
    }

    return JSONResponse(content=result_data)
