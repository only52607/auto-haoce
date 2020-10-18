from fastapi import Depends, FastAPI, HTTPException, status, APIRouter
from pydantic import BaseModel
from haoce import *
from typing import Optional
from routers import auth

router = APIRouter()

@router.get("/info")
async def get_user_info(session:auth.UserSession = Depends(auth.get_current_user_session)):
    return obj2dict(await session.get_user_info())

@router.get("/setting")
async def get_user_setting(session:auth.UserSession = Depends(auth.get_current_user_session)):
    return obj2dict(await session.haoce.get_setting())

