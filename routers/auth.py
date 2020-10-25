from fastapi import Depends, FastAPI, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import JWTError, jwt
from haoce import *
from datetime import datetime, timedelta
from typing import Optional

SECRET_KEY = "09d25e094faa6cf2556c818166b7a9563b93a7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
scheme = OAuth2PasswordBearer(tokenUrl="auth")
router = APIRouter()

class UserSession():
    def __init__(self,haoce:HaoCe,username:str,password:str):
        self.haoce = haoce
        self.username = username
        self.password = password
        self.reading_status = HaoCe.ReadingTaskStatus()

    # 原方法的缓存方法, @ lazy 无法作用于async方法

    async def get_user_info(self):
        try:return self.__user_info
        except:pass
        self.__user_info = await self.haoce.get_user_info()
        return self.__user_info

    async def get_books(self):
        try:return self.__books
        except:pass
        book_list = await self.haoce.get_books()
        self.__books = { book.book_id:book for book in book_list }
        return self.__books
    
    async def get_book(self,book_id):
        books = await self.get_books()
        return books[book_id]

    async def get_book_isbn(self,book_id):
        book = await self.get_book(book_id)
        try:return book._isbn
        except:pass
        book._isbn = await self.haoce.get_book_isbn(book_id)
        book.novel_id = book._isbn.novel_id
        return book._isbn

    async def get_book_novel_id(self,book_id):
        book = await self.get_book(book_id)
        try:return book.novel_id
        except:pass
        await self.get_book_isbn(book_id)
        return book.novel_id

    async def get_book_data(self,book_id):
        book = await self.get_book(book_id)
        try:return book._data
        except:pass
        book._data = await book.get_data()
        book._chapters_dict = {chapter.cp_id:chapter for chapter in book._data.chapters}
        return book._data

    async def get_book_chapters(self,book_id):
        book = await self.get_book(book_id)
        try:return book._chapters_dict
        except:pass
        await self.get_book_data(book_id)
        return book._chapters_dict

    async def get_book_view_data(self,book_id):
        data = await self.get_book_data(book_id)
        return data.view_data

    async def get_chapter_content(self,book_id,cp_id):
        chapters = await self.get_book_chapters(book_id)
        try:return chapters[cp_id]._content
        except:pass
        chapters[cp_id]._content = await chapters[cp_id].get_content()
        return chapters[cp_id]._content

sessions = dict()

async def create_access_token(username:str,password:str,expires_delta: Optional[timedelta] = None):
    if username in sessions:
        if sessions[username].password != password:raise LoginFailedException()
    else:
        haoce = HaoCe(username,password)
        await haoce.login_if_not()
        sessions[username] = UserSession(haoce = haoce,username=username,password=password)

    if expires_delta:expire = datetime.utcnow() + expires_delta
    else: expire = datetime.utcnow() + timedelta(minutes=14400)
    
    return jwt.encode({"exp": expire,"username" : username}, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user_session(token: str = Depends(scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_name = payload.get("username")
        if user_name is None or user_name not in sessions:raise credentials_exception
        user_session = sessions[user_name]
    except JWTError:
        raise credentials_exception
    except Exception:
        raise credentials_exception
    return user_session

@router.post("/")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        token = await create_access_token(form_data.username,form_data.password)
    except LoginFailedException as e:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    except Exception as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return {"access_token": token, "token_type": "bearer"}

@router.delete("/")
async def logout(user_session: UserSession = Depends(get_current_user_session)):
    await user_session.haoce.close()
    sessions.pop(user_session.username)
    del user_session
    return {"message","ok"}