from fastapi import Depends, FastAPI, HTTPException, status, APIRouter, BackgroundTasks
from pydantic import BaseModel
from haoce import *
from typing import Optional,List
from routers import auth
import asyncio
import time

router = APIRouter()

@router.get("/")
async def get_books(session:auth.UserSession = Depends(auth.get_current_user_session)):
    books = await session.get_books()
    return { k:obj2dict(v) for k,v in books.items() }

@router.get("/status")
async def get_reading_status(session:auth.UserSession = Depends(auth.get_current_user_session)):
    return obj2dict(await session.haoce.get_read_status())

@router.get("/reading_task")
async def get_reading_task(session:auth.UserSession = Depends(auth.get_current_user_session)):
    return obj2dict(session.reading_status)

@router.post("/reading_task")
async def post_reading_task(book_id:str,chapters_id:List[str],session:auth.UserSession = Depends(auth.get_current_user_session)):
    if session.reading_status and session.reading_status.is_running:raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail="Task is running!")
    chapters = await session.get_book_chapters(book_id)
    session.reading_status.current_book_id = book_id
    session.reading_status.chapter_list = chapters_id
    async def read_task():
        session.reading_status.is_running = True
        session.reading_status.is_complete = False
        session.reading_status.start_time = int(time.time())
        for index,chapter_id in enumerate(chapters_id):
            session.reading_status.current_chapter_id = chapter_id
            session.reading_status.current_chapter_index = index
            reader = await chapters[chapter_id].get_reader()
            task = reader.get_read_task(status = session.reading_status)
            await task()
        session.reading_status.is_running = False
        session.reading_status.is_complete = True
        session.reading_status.complete_time = int(time.time())
    session.reading_status._current_task = asyncio.create_task(read_task())
    return {"message":"ok"}

@router.delete("/reading_task")
async def cancel_reading_task(session:auth.UserSession = Depends(auth.get_current_user_session)):
    if session.reading_status._current_task:
        try:session.reading_status._current_task.cancel()
        except:pass
    session.reading_status.is_running = False
    return {"message":"ok"}

@router.get("/{book_id}/isbn")
async def get_book_isbn(book_id,session:auth.UserSession = Depends(auth.get_current_user_session)):
    return obj2dict(await session.get_book_isbn(book_id))

@router.get("/{book_id}/data")
async def get_book_data(book_id,session:auth.UserSession = Depends(auth.get_current_user_session)):
    try:
        book = await session.get_book(book_id)
    except:
        raise HTTPException(404,detail="No such book_id")
    return obj2dict(await book.get_data()) 

@router.get("/{book_id}/chapters")
async def get_book_chapters(book_id,session:auth.UserSession = Depends(auth.get_current_user_session)):
    chapters = await session.get_book_chapters(book_id)
    return { k:obj2dict(v) for k,v in chapters.items() }

@router.get("/{book_id}/chapters/{cp_id}")
async def get_book_chapter(book_id,cp_id,session:auth.UserSession = Depends(auth.get_current_user_session)):
    chapters = await session.get_book_chapters(book_id)
    return obj2dict(chapters[chapter_id])

@router.get("/{book_id}/chapters/{cp_id}/content")
async def get_book_chapter_content(book_id,cp_id,session:auth.UserSession = Depends(auth.get_current_user_session)):
    return obj2dict(await session.get_chapter_content(book_id,chapter_id))

@router.get("/{book_id}/chapters_view_data")
async def get_book_chapters_view_data(book_id,session:auth.UserSession = Depends(auth.get_current_user_session)):
    novel_id = await session.get_book_novel_id(book_id)
    chapters_view_data = await session.haoce.get_chapters_view_data(novel_id)
    return { view_data.cp_id:obj2dict(view_data) for k,view_data in chapters_view_data.items()}

@router.get("/{book_id}/view_data")
async def get_book_view_data(book_id,session:auth.UserSession = Depends(auth.get_current_user_session)):
    return obj2dict(await session.get_book_view_data(book_id))