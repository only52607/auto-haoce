import requests,json,time,aiohttp,asyncio,http,os,sys,re
from typing import List

def flatten_dict(raw,root_name = None):
    fdct = dict()
    for k,v in raw.items():
        if root_name == None:
            key_name = k
        else:
            key_name = root_name + '[' + k + ']'
        if isinstance(v,dict):
            fdct.update(flatten_dict(raw = v,root_name = key_name))
        else:
            fdct[key_name] = v
    return fdct

def filter_html_tag(text):
    return re.sub("<[^>]*?>","",text)

def obj2dict(obj):
    if not  hasattr(obj,"__dict__"):
        return obj
    result = {}
    for key, val in obj.__dict__.items():
        if key.startswith("_"):
            continue
        element = []
        if isinstance(val, list):
            for item in val:
                element.append(obj2dict(item))
        else:
            element = obj2dict(val)
        result[key] = element
    return result

class LoginFailedException(Exception):
    pass

class HaoCe:
    class UserInfo:
        def __init__(self,uid,name,school,term,number,college_name,head,**kwargs):
            self.name = name
            self.uid = uid
            self.user_id = uid
            self.school = school
            self.term = term
            self.number = number
            self.college_name = college_name
            self.head = head

    class ReadStatus:
        def __init__(self,novel_cnt,time,word,finish,today,cp,**kwargs):
            self.novel_cnt = novel_cnt
            self.time = time
            self.word = word
            self.finish = finish
            self.cp = cp
            self.today_rank = today['rank']
            self.today_time = today['time_today']
            self.today_view_time = today['view_time']

    class ClassInfo:
        def __init__(self,class_id,stu_cnt,user_id,ctime,task_cnt,**kwargs):
            self.id = class_id
            self.student_cnt = stu_cnt
            self.user_id = user_id
            self.ctime = ctime
            self.task_cnt = task_cnt
            self.type = kwargs['type']
            self.name = kwargs['class']

    class UserSetting:
        def __init__(self,
            term_id,term,user_id,school_id,start_time,end_time,ctime,s_start_time,s_end_time,book_limit,book_limit_min,term_key,end,is_school_user,block_id,
            class_info,**kwargs
        ):
            self.term_id = term_id
            self.term = term
            self.user_id = user_id
            self.school_id = school_id
            self.start_time = start_time
            self.end_time = end_time
            self.s_start_time = s_start_time
            self.s_end_time = s_end_time
            self.book_limit = book_limit
            self.book_limit_min = book_limit_min
            self.end = end
            self.is_school_user = is_school_user
            self.block_id = block_id

            self.class_info = HaoCe.ClassInfo(**class_info)

    class BookInfo:
        def __init__(self,book_id,book,book_info,book_writer,book_img,school,user_cnt,book_pdf,book_page,book_isbn,book_word_cnt,term_key,topic_cnt,ctime,type,haoce = None,**kwargs):
            self.id = book_id
            self.name = book
            self.info = filter_html_tag(book_info)
            self.writer = book_writer
            self.img = book_img
            self.school = school
            self.user_cnt = user_cnt
            self.pdf = book_pdf
            self.page = book_page
            self.isbn = book_isbn
            self.word_cnt = book_word_cnt
            self.term_key = term_key
            self.topic_cnt = topic_cnt
            self.ctime = ctime
            self.type = type
            self.__haoce = haoce
            self.__chapters_view_data = None
        
        def require_haoce(self):
            if (self.__haoce == None): raise Exception("Required Haoce!")

        async def get_isbn(self):
            self.require_haoce()
            return await self.__haoce.get_book_isbn(self.id)

        async def get_novel_id(self):
            isbn = await self.get_isbn()
            return isbn.novel_id

        async def get_data(self):
            self.require_haoce()
            isbn = await self.get_isbn()
            return await self.__haoce.get_book_data(self.id,isbn.novel_id,haoce = self.__haoce,book_info = self)

        async def get_chapters_view_data(self):
            self.require_haoce()
            isbn = await self.get_isbn()
            self.__chapters_view_data = await self.__haoce.get_chapters_view_data(isbn.novel_id)
            return self.__chapters_view_data

        async def get_chapter_view_data(self,cp_id):
            if (self.__chapters_view_data == None): await self.get_chapters_view_data()
            if cp_id in self.__chapters_view_data:
                return self.__chapters_view_data[cp_id]
            return None

        async def get_chapters(self):
            self.require_haoce()
            data = await self.get_data()
            return data.chapters

        async def get_view_data(self):
            self.require_haoce()
            data = await self.get_data()
            return data.view_data

    class BookIsbn:
        def __init__(self,isbn_id,book_isbn,book,book_writer,book_info,user_id,publishing_time,language,difficult_rank,novel_id,**kwargs):
            self.id = isbn_id
            self.book_isbn = book_isbn
            self.name = book
            self.writer = book_writer
            self.info = book_info
            self.user_id = user_id
            self.publishing_time = publishing_time
            self.language = language
            self.difficult_rank = difficult_rank
            self.novel_id = novel_id

    class UserBookInfo:
        def __init__(self,id,user_id,book_id,ctime,type,class_id,classes,haoce = None,**kwargs):
            self.id = id
            self.user_id = user_id
            self.ctime = ctime
            self.type = type
            self.book_id = book_id
            self.class_id = class_id
            self.class_info = HaoCe.ClassInfo(**classes[class_id])
            self.book_info = HaoCe.BookInfo(**kwargs['book_id_merge'],haoce = haoce)
        
        async def get_isbn(self):
            return await self.book_info.get_isbn()
        
        async def get_data(self):
            return await self.book_info.get_data()

        async def get_chapters_view_data(self):
            return await self.book_info.get_chapters_view_data()

        async def get_chapters(self):
            return await self.book_info.get_chapters()
        
        async def get_view_data(self):
            return await self.book_info.get_view_data()

    class Chapter:
        def __init__(self,cp_id,site_id,chapter_id,chapter,mp3,mp3_local,view,word,good_cnt,comment,del_time,raw_data,book_id,book_info = None,haoce=None,**kwargs):
            self.cp_id = cp_id
            self.site_id = site_id
            self.chapter_id = chapter_id
            self.chapter = chapter
            self.mp3 = mp3
            self.mp3_local = mp3_local
            self.view = view
            self.word = word
            self.good_cnt = good_cnt
            self.comment = comment
            self.del_time = del_time
            self.book_id = book_id
            self.raw_data = raw_data
            self.__haoce = haoce
            self.__book_info = book_info
        
        def require_haoce(self):
            if (self.__haoce == None): raise Exception("Required Haoce!")
        
        def require_book_info(self):
            if (self.__book_info == None): raise Exception("Required BookInfo!")

        async def get_view_data(self):
            self.require_book_info()
            return await self.__book_info.get_chapter_view_data(self.cp_id)

        async def get_content(self):
            self.require_book_info()
            self.require_haoce()
            book_data = await self.__book_info.get_data()
            novel_raw_data = book_data.novel.raw_data
            content = await self.__haoce.get_chapter_content(novel_raw_data = novel_raw_data,cp_id = self.cp_id)
            return content

        async def get_novel_id(self):
            self.require_book_info()
            return await self.__book_info.get_novel_id()

        async def get_reader(self):
            self.require_book_info()
            await self.__book_info.get_chapters_view_data()
            reader = HaoCe.ChapterReader(haoce = self.__haoce,chapter = self)
            await reader.init()
            return reader

    class ChapterContent:
        def __init__(self,id,title,contents,**kwargs):
            self.id = id
            self.title = title
            self.content_list = contents
            self.content_list_cn = filter(lambda item:item['lg']=='cn',contents)
            self.content_list_en = filter(lambda item:item['lg']=='en',contents)
            self.content_cn = ''.join(list(map(lambda item:item['text'],self.content_list_cn)))
            self.content_en = ''.join(list(map(lambda item:item['text'],self.content_list_en)))

    class BookViewData:
        def __init__(self,id,user_id,novel_id,school_id,dtime,ctime,last_time,term_key,progress,cp_cnt,last_cp_id,word,type,block_id,**kwargs):
            self.id = id
            self.user_id = user_id
            self.novel_id = novel_id
            self.school_id = school_id
            self.dtime = dtime
            self.ctime = ctime
            self.last_time = last_time
            self.term_key = term_key
            self.progress = progress
            self.cp_cnt = cp_cnt
            self.last_cp_id = last_cp_id
            self.word = word
            self.type = type
            self.block_id = block_id

    class ChapterViewData:
        def __init__(self,view_id,novel_id,cp_id,user_id,ctime,dtime,word,school_id,term_key,progress,last,last_time,**kwargs):
            self.view_id = view_id
            self.novel_id = novel_id
            self.cp_id = cp_id
            self.user_id = user_id
            self.ctime = ctime
            self.dtime = dtime
            self.word = word
            self.school_id = school_id
            self.term_key = term_key
            self.progress = progress
            self.last = last
            self.last_time = last_time

    class BookData:
        def __init__(self,chapters,view_data,novel):
            self.chapters = chapters
            self.view_data = view_data
            self.novel = novel

    class Novel:
        def __init__(self,novel_id,site_id,novel,cp,cdn_img,ctime,raw_data,**kwargs):
            self.novel_id = novel_id
            self.site_id = site_id
            self.novel = novel
            self.cp = cp
            self.cdn_img = cdn_img
            self.ctime = ctime
            self.raw_data = raw_data

    class ChapterReader:
        def __init__(self,haoce,chapter):
            self.__haoce = haoce
            self.__chapter = chapter

        async def init(self) -> bool:
            self.__page_count = 20
            self.__novel_id = await self.__chapter.get_novel_id()
            view_data = await self.__chapter.get_view_data()
            if view_data == None:
                self.__dtime = 0
                await self.__haoce.do_chapter_view(
                    chapter_raw_data = self.__chapter.raw_data,
                    dtime = 1,
                    count = 0,
                    page = 0,
                    page_count = self.__page_count,
                    novel_id = self.__novel_id
                )
                return False
            self.__dtime = int(view_data.dtime)
            return True

        async def do_view(self,time,page):
            self.__dtime += time
            await self.__haoce.do_chapter_view(
                chapter_raw_data = self.__chapter.raw_data,
                dtime = self.__dtime,
                count = time,
                page = page,
                page_count = self.__page_count,
                novel_id = self.__novel_id
            )
        
        def get_dtime(self):
            return self.__dtime
        
        def set_page_count(self,page_count):
            self.__page_count = page_count

        def get_page_count(self):
            return self.__page_count

        def get_read_task(
            self,
            start_page = 0,
            end_page = None,
            read_time_generater = lambda page: 90,
            before_read_page = lambda page,time : None,
            after_read_page = lambda page,time : None,
            callback = lambda : None,
            status = None
        ):
            if end_page == None:end_page = self.__page_count + 1
            if start_page < 0:raise Exception("start_page must greater than 0!")
            if start_page > end_page:raise Exception("start_page less than end_page!")
            if end_page > self.__page_count + 1:raise Exception("end_page must less than page_count!")
            if not status:status = HaoCe.ReadingTaskStatus()
            async def task():
                status.current_page_count = end_page - start_page
                for page in range(start_page,end_page):
                    status.current_page = page
                    page_read_time = read_time_generater(page)
                    before_read_page(page,page_read_time)
                    await asyncio.sleep(page_read_time)
                    await self.do_view(time = page_read_time,page = page)
                    after_read_page(page,time)
                callback()
            return task

    class ReadingTaskStatus:
        def __init__(self):
            self.is_running = False
            self.is_complete = False
            self.start_time = 0
            self.complete_time = 0
            self.current_book_id = 0
            self.chapter_list = []
            self.current_chapter_index = 0
            self.current_chapter_id = 0
            self.current_page = 0
            self.current_page_count = 0
            self._current_task = None

    def __init__(self,username,password):
        self.__session = requests.session()
        self.__base_url = "https://appclient.haoce.com"
        self.__username  = username
        self.__password = password
        self.__cookie_file = __file__[:__file__.rfind("\\")] + "\cookies\cookies_" + str(username)
        self.__cookie_jar = aiohttp.CookieJar(unsafe=True)
        try:
            self.__cookie_jar.load(self.__cookie_file)
        except:
            pass
        self.__session = aiohttp.ClientSession(cookie_jar = self.__cookie_jar)

        self.__user_info = None

    async def __aenter__(self):
        await self.login_if_not()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    def __get_dict_mb(self,extras = {}):
        result = {
            "MB_time":int(time.time()),
            "MB_version":"1.2.8",
            "MB_os[android]":True,
            "MB_os[version]":10,
            "MB_os[isBadAndroid]":False,
            "MB_os[plus]":True,
            "MB_uuid":""
        }
        result.update(extras)
        return result

    def __get_dict_push(self,extras = {}):
        result = {
            "push_cid":"c449c991aa6ec04b1c639dc6ef6d4db2",
            "push_token":"c449c991aa6ec04b1c639dc6ef6d4db2"
        }
        result.update(extras)
        return result

    def __get_dict_login(self,extras = {}):
        result = {
            "openid":int(self.__username),
            "psw":self.__password
        }
        result.update()
        return result

    def __get_dict_default_headers(self,extras = {}):
        headers = {
            "Accept": "application/json",
            "Sec-Fetch-Dest": "empty",
            "X-Display": "json",
            "Origin": "https://appclient.haoce.com",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://appclient.haoce.com/app/page/v2home",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; RMX1901 Build/QKQ1.190918.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.99 Mobile Safari/537.36 Html5Plus/1.0 (Immersed/32.0)",
            "Content-Type": "application/x-www-form-urlencoded",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
        }
        headers.update(extras)
        return headers

    async def close(self):
        await self.__session.close()

    async def login(self):
        post_data = {
            "MB_wid":"app.haoce.com"
        }
        post_data.update(self.__get_dict_login())
        post_data.update(self.__get_dict_push())
        post_data.update(self.__get_dict_mb())
        headers = self.__get_dict_default_headers({
            "Origin": "file://",
            "Sec-Fetch-Site": "cross-site"
        })
        async with self.__session.post(self.__base_url + "//app/login/post",data=post_data,headers=headers) as response:
            self.__cookie_jar.save(self.__cookie_file)
            response_json = await response.json()
            if response_json['error'] != 0: 
                await self.close()
                raise LoginFailedException()
            return response_json

    async def check_open_id(self):
        post_data = {
            "MB_wid":"haoce_main_v2"
        }
        post_data.update(self.__get_dict_push())
        post_data.update(self.__get_dict_mb())
        async with self.__session.post(self.__base_url + "/quiz/checkopenid",data=post_data,headers=self.__get_dict_default_headers()) as response:
            response_json = await response.json()
            if 'redirect' not in response_json:
                self.__user_info = self.UserInfo(**response_json['data']['_cu'])
            return response_json

    async def login_if_not(self):
        response = await self.check_open_id()
        if 'redirect' in response:
            print("账号未登录，正在登录。")
            await self.login()
    
    async def get_user_info(self) -> UserInfo:
        if self.__user_info == None:
            await self.check_open_id()
        return self.__user_info
    
    async def get_read_status(self) -> ReadStatus:
        async with self.__session.post(self.__base_url + "//book/me/v2me",data=self.__get_dict_mb(),headers=self.__get_dict_default_headers({
            "Referer": "https://appclient.haoce.com/app/page/v2home",
        })) as response:
            response_json = await response.json()
            return self.ReadStatus(**response_json['data']['tj']['view'],today = response_json['data']['tj']['today'])
    
    async def get_setting(self) -> UserSetting:
        async with self.__session.post(self.__base_url + "//member/setting",data=self.__get_dict_mb(),headers=self.__get_dict_default_headers({
            "Referer": "https://appclient.haoce.com/app/page/v2me",
        })) as response:
            response_json = await response.json()
            return self.UserSetting(**response_json['data']['term_conf'],class_info = response_json['data']['me']['class_info'])

    async def get_books(self) -> List[UserBookInfo]:
        post_data = {
            "MB_wid":"v2bookMy"
        }
        post_data.update(self.__get_dict_mb())
        post_data.update(self.__get_dict_push())
        headers = self.__get_dict_default_headers({
            "Referer": "https://appclient.haoce.com/app/page/v2bookMy",
        })
        async with self.__session.post(self.__base_url + "/book/user/?block_id=0",data=post_data,headers=headers) as response:
            response_json = await response.json()
            return list(map(lambda data:self.UserBookInfo(**data,classes=response_json['data']['class'],haoce = self),response_json['data']['me_book']))

    async def get_book_isbn(self,book_id) -> BookIsbn:
        post_data = {
            "MB_wid":"v2bookMy"
        }
        post_data.update(self.__get_dict_push())
        post_data.update(self.__get_dict_mb())
        async with self.__session.post(self.__base_url + "/app/bookOne/detail/" + book_id,data=post_data,headers=self.__get_dict_default_headers({
            "Referer": "https://appclient.haoce.com/app/page/bookOne",
        })) as response:
            response_json = await response.json()
            return self.BookIsbn(**response_json['data']['book']['isbn'])

    async def get_book_data(self,book_id,novel_id,haoce = None,book_info = None) -> BookData:
        post_data = {
            "MB_wid":"bookOne"
        }
        post_data.update(self.__get_dict_mb())
        post_data.update(self.__get_dict_push())
        headers = self.__get_dict_default_headers({
            "Referer": "https://appclient.haoce.com/app/page/readerFull",
        })
        async with self.__session.post(self.__base_url + "/book/novel/listV2?id=" + novel_id + "&book_id=" + book_id,data=post_data,headers=headers) as response:
            response_json = await response.json()
            view_data = self.BookViewData(**response_json['data']['novel']['viewList'])
            novel = self.Novel(**response_json['data']['novel']['novel'],raw_data=response_json['data']['novel']['novel'])
            chapters = list(map(lambda chapter_json:self.Chapter(**chapter_json,raw_data=chapter_json,book_id=book_id,haoce=haoce,book_info=book_info),response_json['data']['novel']['chapter']))
            return self.BookData(chapters = chapters,view_data = view_data,novel=novel)

    async def get_chapters_view_data(self,novel_id) -> List[ChapterViewData]:
        post_data = {
            "MB_wid":"bookOne"
        }
        post_data.update(self.__get_dict_mb())
        post_data.update(self.__get_dict_push())
        headers = self.__get_dict_default_headers({
            "Referer": "https://appclient.haoce.com/app/page/readerFull",
        })
        async with self.__session.post(self.__base_url + "/book/novel/getView/" + novel_id,data=post_data,headers=headers) as response:
            response_json = await response.json()
            chapters_view_data_list = list(map(lambda data:self.ChapterViewData(**data),response_json['data']['vList'].values()))
            return dict(map(lambda data:(data.cp_id,data),chapters_view_data_list))

    async def get_chapter_content(self,novel_raw_data,cp_id) -> ChapterContent:
        post_data = {}
        post_data.update(flatten_dict(raw = novel_raw_data,root_name = 'novel'))
        post_data.update(self.__get_dict_push())
        post_data.update(self.__get_dict_mb({
            "MB_wid":"readerFull"
        }))
        async with self.__session.post(self.__base_url + "/book/novel/chapter/" + cp_id,data=post_data,headers=self.__get_dict_default_headers({
            "Referer": "https://appclient.haoce.com/app/page/readerFull",
        })) as response:
            response_json = await response.json()
            return self.ChapterContent(**response_json['data']['chapter'])

    async def do_chapter_view(self,chapter_raw_data,dtime,count,page,page_count,novel_id):
        post_data = {
            'dtime':dtime,
            'count_v2':count,
            'page':page,
            'page_count':page_count,
            'novel_id':novel_id,
            'block_id':0
        }
        post_data.update(chapter_raw_data)
        post_data.update(self.__get_dict_push())
        post_data.update(self.__get_dict_mb({
            "MB_wid":"readerFull"
        }))
        async with self.__session.post(self.__base_url + "/book/novel/doViewV2",data=post_data,headers=self.__get_dict_default_headers({
            "Referer": "https://appclient.haoce.com/app/page/readerFull",
        })) as response:
            response_json = await response.json()
            return response_json