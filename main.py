from starlette.templating import Jinja2Templates
from traceback import format_exc
from enum import Enum
from core import *

template = Jinja2Templates("./static")
TemplateResponse = template.TemplateResponse


class Universities(Enum):
    BNU = "北师大"
    FuJen = "辅大"
    BFHNC = "女高师"

    @property
    def name(self):
        return University(self.value).full_name


@app.get("/api/{university}", tags=["API"])
@fine_log
@cache_with_etag
def get_university_md(request: Request, university: Universities):
    try:
        html = University(university.value).html
        return ORJSONResponse({
            "div": template.get_template("div_article.xml").render({"name": university.name, "markdown": html}),
            "title": university.name
        })

    except NotADirectoryError:
        return ORJSONResponse(format_exc(chain=False), 404)


@app.get("/{university}", responses={200: {"content": {"text/html": {}}}})
@fine_log
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
@fine_log
@cache_with_etag
def get_person_md(request: Request, university: Universities, category: Categories, name: str):
    try:
        person = Person(name, University(university.value), category.value)
        html = person.html
        return ORJSONResponse({
            "div": template.get_template("div_article.xml").render({"name": name, "markdown": html}),
            "title": f"{name} - {university.value}{category.value}"
        })

    except (NotADirectoryError, FileNotFoundError):
        return PlainTextResponse(format_exc(chain=False), 404)


@app.get("/{university}/{category}/{name}", responses={
    200: {"content": {"text/html": {}}}, 404: {"content": {"text/plain": {}}}
})
@fine_log
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
