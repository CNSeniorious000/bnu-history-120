from traceback import format_exc
from contextlib import suppress
from fastapi import APIRouter
from core import *

router = APIRouter(include_in_schema=False)


@router.get("/{university}")
def get_university_info(request: Request, university: Universities):
    with suppress(NotADirectoryError):
        html = University(university.value).html
        return TemplateResponse("person.jinja2", {
            "request": request,
            "title": university.name,
            "name": university.name,
            "markdown": html,
        })

    return ORJSONResponse(format_exc(chain=False), 404)


@router.get("/{university}/{category}/{name}")
def get_person_info(request: Request, university: Universities, category: Categories, name: str):
    with suppress(NotADirectoryError, FileNotFoundError):
        person = Person(name, University(university.value), category.value)
        html = person.html
        return TemplateResponse("person.jinja2", {
            "request": request,
            "name": name,
            "title": f"{name} - {university.value}{category.value}",
            "markdown": html,
        })

    return PlainTextResponse(format_exc(chain=False), 404)
