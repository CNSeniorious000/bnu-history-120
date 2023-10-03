from collections import defaultdict
from contextlib import suppress
from functools import lru_cache
from traceback import format_exc
from typing import Dict, List, Literal

from fastapi import APIRouter
from fastapi.responses import ORJSONResponse, PlainTextResponse
from pydantic import AnyHttpUrl

from core import template
from person import Categories, Universities, people, render_person_html, render_university_html, universities

router = APIRouter(prefix="/api", tags=["API"])


@router.get("/people/list", response_model=List[str])
@lru_cache(None)
def get_name_set():
    return ORJSONResponse(list({person.name for person in people}))


@router.get("/people/dict", response_model=Dict[str, AnyHttpUrl])
@lru_cache(None)
def get_people_map():
    name_map = defaultdict(list)
    for person in people:
        name_map[person.name].append(person.url)

    return ORJSONResponse(name_map)


@router.get("/{university}", response_model=Dict[Literal["div", "title"], str])
def get_university_md(university: Universities):
    with suppress(NotADirectoryError):
        html = render_university_html(university)
        university_full_name = universities[university].full_name
        return ORJSONResponse(
            {
                "div": template.get_template("Article.jinja2").render(
                    {"name": university_full_name, "markdown": html}
                ),
                "title": university_full_name,
            }
        )

    return PlainTextResponse(format_exc(chain=False), 404)


@router.get("/{university}/{category}/{name}", response_model=Dict[Literal["div", "title"], str])
def get_person_md(university: Universities, category: Categories, name: str):
    with suppress(NotADirectoryError, FileNotFoundError):
        html = render_person_html(name, university, category)
        return ORJSONResponse(
            {
                "div": template.get_template("Article.jinja2").render(
                    {"name": name, "markdown": html}
                ),
                "title": f"{name} - {university}{category}",
            }
        )

    return PlainTextResponse(format_exc(chain=False), 404)
