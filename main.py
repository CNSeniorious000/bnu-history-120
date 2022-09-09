from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from urllib.parse import urlparse
from brotli_asgi import BrotliMiddleware
from traceback import format_exc
from fastapi.responses import *
from fastapi import FastAPI
from enum import Enum
from person import *
from tools import *

app = FastAPI(title="BNU 120 years 🎉", description=open("readme.md", encoding="utf-8").read(), version="dev",
              contact={"name": "Muspi Merol", "url": "https://muspimerol.site/", "email": "admin@muspimerol.site"})
app.add_middleware(BrotliMiddleware, quality=11)
app.mount("/icon/", StaticFiles(directory="./static/icon/"))


@app.get("/robots.txt", responses={200: {"content": {"text/plain": {}}}})
@fine_log
def on_scraper(request: Request):
    print(request.headers)
    return PlainTextResponse("User-agent: *\nAllow: /")


@app.get("/favicon.ico", include_in_schema=False)
@fine_log
def get_favicon_ico(request: Request):
    return RedirectResponse("/icon/favicon.ico")


@app.get("/", include_in_schema=False)
@fine_log
def get_temporary_redirect(request: Request):
    return RedirectResponse("/北师大")


@app.get("/{filename}.css", include_in_schema=False)
@fine_log
@cache_with_etag
def render_css(request: Request, filename: str):
    main_css_path = f"./static/{filename}.css"
    if isfile(main_css_path):
        if isfile(light_css_path := f"./static/{filename}-light.css") \
                and isfile(dark_css_path := f"./static/{filename}-dark.css"):
            """生成聚合css"""
        else:
            return Response(open(main_css_path).read(), media_type="text/css")
    else:
        return PlainTextResponse(f"{main_css_path} is not a file", 404)

    # generate mixed style sheet

    main = open(main_css_path).read()
    light = open(light_css_path).read()
    dark = open(dark_css_path).read()

    return Response("\n".join((
        main,
        "@media (prefers-color-scheme: light) {", light, "}",
        "@media (prefers-color-scheme: dark) {", dark, "}"
    )), media_type="text/css")


@app.get("/{filename}.svg", include_in_schema=False)
@fine_log
@cache_with_etag
def get_svg_asset(request: Request, filename: str):
    try:
        path = unquote(urlparse(request.headers["referer"]).path, "utf-8").removeprefix("/")
    except KeyError:
        return PlainTextResponse("you can't get a svg without a referer header", 400)
    full_path = f"./data/{path}/{filename}.svg"
    if isfile(full_path):
        return Response(open(full_path, encoding="utf-8").read(), media_type="image/svg+xml")
    else:
        return PlainTextResponse(f"{full_path} is not a file", 404)


template = Jinja2Templates("./static")
TemplateResponse = template.TemplateResponse


class Universities(Enum):
    BNU = "北师大"
    FuJen = "辅大"
    BFHNC = "女高师"

    @property
    def name(self):
        return University(self.value).full_name


@app.get("/{university}", responses={200: {"content": {"text/html": {}}}})
@fine_log
@cache_with_etag
def get_university_info(request: Request, university: Universities):
    try:
        html = University(university.value, []).html
        return TemplateResponse("article_view.html", {
            "request": request,
            "title": university.name,
            "name": university.name,
            "markdown": html,
            "universities": University.universities
        })

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
@fine_log
@cache_with_etag
def get_person_info(request: Request, university: Universities, category: Categories, name: str):
    try:
        person = Person(name, University(university.value, []), category.value)
        html = person.html
        return TemplateResponse("article_view.html", {
            "request": request,
            "name": name,
            "title": f"{name} - {university.value}{category.value}",
            "markdown": html,
            "universities": University.universities
        })

    except (NotADirectoryError, FileNotFoundError):
        return PlainTextResponse(format_exc(chain=False), 404)
