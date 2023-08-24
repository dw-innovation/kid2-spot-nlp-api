import torch
from pydantic import BaseModel, validator
from typing import Dict, List
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from models.op_plus import inference

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Query(BaseModel):
    action: str
    nodes: List
    relations: List


class Response(BaseModel):
    op_query: Dict


# @app.post("/translate_from_dict_to_op", response_model=Response)
# def translate_from_dict_to_op(query: Query):
#     query = query.dict()
#     return dict(op_query=TEMPLATES[query["action"]].generate_op_query(query))


@app.get("/translate_from_nl_to_op", response_model=Response)
@torch.inference_mode()
def translate_from_nl_to_op(sentence: str):
    output = inference(sentence)
    return dict(op_query=output)
