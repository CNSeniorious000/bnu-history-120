from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from urllib.parse import urlparse, unquote
from brotli_asgi import BrotliMiddleware
from starlette.requests import Request
from traceback import format_exc
from fastapi.responses import *
from fastapi import FastAPI
from hashlib import md5
from enum import Enum
from person import *

app = FastAPI(title="BNU 120 years 🎉", description=open("readme.md", encoding="utf-8").read(), version="dev",
              contact={"name": "Muspi Merol", "url": "https://muspimerol.site/", "email": "admin@muspimerol.site"})
app.add_middleware(BrotliMiddleware, quality=11)
app.mount("/icon/", StaticFiles(directory="./static/icon/"))


@app.get("/robots.txt", responses={200: {"content": {"text/plain": {}}}})
def on_scraper(request: Request):
    print(request.headers)
    return PlainTextResponse("User-agent: *\nAllow: /")


@app.get("/favicon.ico", include_in_schema=False, response_class=FileResponse)
def get_favicon_ico():
    return "./static/icon/favicon.ico"


@app.get("/{filename}.css", include_in_schema=False)
def get_common_css(filename: str):
    full_path = f"./static/{filename}.css"
    if isfile(full_path):
        return FileResponse(full_path)
    else:
        return PlainTextResponse(f"{full_path} is not a file", 404)


@app.get("/{filename}.svg", include_in_schema=False)
def get_svg_asset(request: Request, filename: str):
    try:
        path = unquote(urlparse(request.headers["referer"]).path, "utf-8").removeprefix("/")
    except KeyError:
        return PlainTextResponse("you can't get a svg without a referer header", 400)
    full_path = f"./data/{path}/{filename}.svg"
    if isfile(full_path):
        return FileResponse(full_path)
    else:
        return PlainTextResponse(f"{full_path} is not a file", 404)


def add_etag(response: Response):
    response.headers["ETag"] = f'W/"{md5(response.body).hexdigest()}"'
    return response


template = Jinja2Templates("./static")
TemplateResponse = template.TemplateResponse


class Universities(Enum):
    BNU = "北师大"
    FuJen = "辅大"
    BFHNC = "女高师"

    @property
    def name(self):
        match self:
            case self.BNU:
                return "北京师范大学"
            case self.FuJen:
                return "辅仁大学"
            case self.BFHNC:
                return "北京女子高等师范学校"


@app.get("/{university}", responses={200: {"content": {"text/html": {}}}})
def get_university_info(request: Request, university: Universities):
    try:
        html = University(university.value, []).html
        return add_etag(TemplateResponse("person.html", {
            "request": request,
            "title": university.name,
            "markdown": html
        }))

    except NotADirectoryError:
        return ORJSONResponse(format_exc(chain=False), 422)


class Categories(Enum):
    president = "校长"
    graduate = "校友"
    teacher = "教师"
    founder = "创始人"


@app.get("/{university}/{category}/{name}", responses={
    200: {"content": {"text/html": {}}}, 404: {"content": {"text/plain": {}}}
})
def get_person_info(request: Request, university: Universities, category: Categories, name: str):
    try:
        person = Person(name, University(university.value, []), category.value)
        html = person.html
        return add_etag(TemplateResponse("person.html", {
            "request": request,
            "title": f"{name} - {university.value}{category.value}",
            "markdown": html
        }))

    except (NotADirectoryError, FileNotFoundError):
        return PlainTextResponse(format_exc(chain=False), 404)
