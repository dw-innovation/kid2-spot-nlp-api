import json
import torch
from pydantic import BaseModel, validator
from templates.factory import TEMPLATES
from typing import Dict, List
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


class Query(BaseModel):
    action: str
    nodes: List
    relations: List


class Response(BaseModel):
    op_query: str
