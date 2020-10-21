from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from haoce import *
from typing import Optional
from routers import auth,user,book
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message":"Hello World!"}

not_found_exception = {404: {"description": "Not found"}}

app.include_router(
    auth.router,
    prefix="/auth",
    responses = not_found_exception
)

app.include_router(
    user.router,
    prefix="/user",
    responses = not_found_exception
)

app.include_router(
    book.router,
    prefix="/books",
    responses = not_found_exception
)