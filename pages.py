from contextlib import suppress
from traceback import format_exc

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse

from core import TemplateResponse
from person import Categories, Universities, render_person_html, render_university_html, universities

router = APIRouter(include_in_schema=False)


@router.get("/{university}")
def get_university_info(request: Request, university: Universities):
    with suppress(NotADirectoryError):
        html = render_university_html(university)
        university_full_name = universities[university].full_name
        return TemplateResponse(
            "person.jinja2",
            {
                "request": request,
                "title": university_full_name,
                "name": university_full_name,
                "markdown": html,
            },
        )

    return PlainTextResponse(format_exc(chain=False), 404)


@router.get("/{university}/{category}/{name}")
def get_person_info(request: Request, university: Universities, category: Categories, name: str):
    with suppress(NotADirectoryError, FileNotFoundError):
        html = render_person_html(name, university, category)
        return TemplateResponse(
            "person.jinja2",
            {
                "request": request,
                "name": name,
                "title": f"{name} - {university}{category}",
                "markdown": html,
            },
        )

    return PlainTextResponse(format_exc(chain=False), 404)
