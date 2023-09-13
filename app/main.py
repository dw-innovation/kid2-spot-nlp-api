from fastapi.responses import JSONResponse
import torch
from pydantic import BaseModel
from typing import Dict
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from models.spot import inference
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

app = FastAPI()

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
        return JSONResponse(
            content={
                "imr": output["result"],
                "rawOutput": output["raw"],
                "status": "success",
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
