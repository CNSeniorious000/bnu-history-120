from contextlib import suppress
from traceback import format_exc

from fastapi import APIRouter

from core import *

router = APIRouter(prefix="/api", tags=["API"])


@router.get("/people/list")
@lru_cache(None)
def get_name_set():
    return ORJSONResponse(list({person.name for person in University.get_all_people()}))


@router.get("/people/dict")
@lru_cache(None)
def get_people_map():
    name_map = {}
    for person in University.get_all_people():
        if path_list := name_map.get(person.name):
            path_list.append(f"/{person.university}/{person.category}/{person.name}")
        else:
            name_map[person.name] = [
                f"/{person.university}/{person.category}/{person.name}"
            ]

    return ORJSONResponse(name_map)


@router.get("/{university}")
def get_university_md(university: Universities):
    with suppress(NotADirectoryError):
        html = University(university.value).html
        return ORJSONResponse(
            {
                "div": template.get_template("Article.jinja2").render(
                    {"name": university.name, "markdown": html}
                ),
                "title": university.name,
            }
        )

    return ORJSONResponse(format_exc(chain=False), 404)


@router.get("/{university}/{category}/{name}")
def get_person_md(university: Universities, category: Categories, name: str):
    with suppress(NotADirectoryError, FileNotFoundError):
        person = Person(name, University(university.value), category.value)
        html = person.html
        return ORJSONResponse(
            {
                "div": template.get_template("Article.jinja2").render(
                    {"name": name, "markdown": html}
                ),
                "title": f"{name} - {university.value}{category.value}",
            }
        )

    return PlainTextResponse(format_exc(chain=False), 404)
