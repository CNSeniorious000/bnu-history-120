from brotli_asgi import BrotliMiddleware
from starlette.requests import Request
from traceback import format_exc
from fastapi.responses import *
from fastapi import FastAPI
from hashlib import md5
from enum import Enum
from person import *

app = FastAPI(title="BNU 120 years 🎉", description=open("readme.md", encoding="utf-8").read(), version="dev")
app.add_middleware(BrotliMiddleware, quality=11)


@app.get("/robots.txt", responses={200: {"content": {"text/plain": {}}}})
def on_scraper(request: Request):
    print(request.headers)
    return PlainTextResponse("User-agent: *\nAllow: /")


def add_etag(response: Response):
    response.headers["ETag"] = f'W/"{md5(response.body).hexdigest()}"'


class Universities(Enum):
    BNU = "北师大"
    FuJen = "辅大"
    BFHNC = "女高师"


@app.get("/{university}", responses={200: {"content": {"text/html": {}}}})
def get_university_info(university: Universities):
    try:
        html = University(university.value, []).html
        add_etag(response := HTMLResponse(html))
        return response
    except NotADirectoryError:
        return ORJSONResponse(format_exc(chain=False), 422)


class Categories(Enum):
    president = "校长"
    graduate = "校友"
    teacher = "教师"
    founder = "创始人"


@app.get("/{university}/{category}/{person}", responses={
    200: {"content": {"text/html": {}}}, 404: {"content": {"text/plain": {}}}
})
def get_person_info(university: Universities, category: Categories, name: str):
    try:
        person = Person(name, University(university.value, []), category.value)
        html = person.html
        add_etag(response := HTMLResponse(html))
        return response
    except (NotADirectoryError, FileNotFoundError):
        return PlainTextResponse(format_exc(chain=False), 404)
