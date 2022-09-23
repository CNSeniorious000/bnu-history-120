from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from traceback import format_exc
from contextlib import suppress
from fastapi import Header
from enum import Enum
from core import *

template = Jinja2Templates("./static")
TemplateResponse = template.TemplateResponse
app.mount("/static/", StaticFiles(directory="./static/"))


@app.get("/api/people.json", tags=["API"])
@cache_with_etag
def get_all_people(request: Request):
    return ORJSONResponse({
        person.name: f"/{person.university}/{person.category}/{person.name}"
        for person in University.get_all_people()
    })


class Universities(Enum):
    BNU = "北师大"
    FuJen = "辅大"
    BFHNC = "女高师"

    @property
    def name(self):
        return University(self.value).full_name


@app.get("/api/{university}", tags=["API"])
@cache_with_etag
def get_university_md(request: Request, university: Universities, x_bnu120_usage: str = Header()):
    if x_bnu120_usage != "preload":
        return PlainTextResponse("please contact me at admin@muspimerol.site before using our open APIs", 400)

    with suppress(NotADirectoryError):
        html = University(university.value).html
        return ORJSONResponse({
            "div": template.get_template("div_article.xml").render({"name": university.name, "markdown": html}),
            "title": university.name
        })

    return ORJSONResponse(format_exc(chain=False), 404)


@app.get("/about", include_in_schema=False)
def about_page(request: Request):
    return TemplateResponse("article_view.html", {
        "request": request,
        "non_preload": True,
        "title": "🏗 under construction",
        "name": "readme.md",
        "markdown": markdown_path("./readme.md", extras=extras),
        "universities": University.universities
    })


@app.get("/{university}", responses={200: {"content": {"text/html": {}}}})
@cache_with_etag
def get_university_info(request: Request, university: Universities):
    try:
        html = University(university.value).html
        return TemplateResponse("article_view.html", {
            "request": request,
            "title": university.name,
            "name": university.name,
            "markdown": html,
            "universities": University.universities
        })

    except NotADirectoryError:
        return ORJSONResponse(format_exc(chain=False), 404)


class Categories(Enum):
    president = "校长"
    graduate = "校友"
    teacher = "教师"
    founder = "创始人"


@app.get("/api/{university}/{category}/{name}", tags=["API"])
@cache_with_etag
def get_person_md(request: Request, university: Universities, category: Categories, name: str,
                  x_bnu120_usage: str = Header()):
    if x_bnu120_usage != "preload":
        return PlainTextResponse("please contact me at admin@muspimerol.site before using our open APIs", 400)

    with suppress(NotADirectoryError, FileNotFoundError):
        person = Person(name, University(university.value), category.value)
        html = person.html
        return ORJSONResponse({
            "div": template.get_template("div_article.xml").render({"name": name, "markdown": html}),
            "title": f"{name} - {university.value}{category.value}"
        })

    return PlainTextResponse(format_exc(chain=False), 404)


@app.get("/{university}/{category}/{name}", responses={
    200: {"content": {"text/html": {}}}, 404: {"content": {"text/plain": {}}}
})
@cache_with_etag
def get_person_info(request: Request, university: Universities, category: Categories, name: str):
    try:
        person = Person(name, University(university.value), category.value)
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


@app.get("/", include_in_schema=False)
def home_page(request: Request):
    return RedirectResponse("/about", 302)
    # return FileResponse("./static/index.html")
