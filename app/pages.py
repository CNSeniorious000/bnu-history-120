from contextlib import suppress
from functools import cache
from traceback import format_exc
from xml.etree.ElementTree import Element, SubElement, tostring

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse, RedirectResponse

from .data import people, render_person_html, render_university_html, universities
from .misc import TemplateResponse
from .models import Categories, Names, Universities

router = APIRouter(include_in_schema=False)


@router.get("/sitemap.xml")
@cache
def get_sitemap():
    urlset = Element("urlset")
    urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

    # Home page
    url = SubElement(urlset, "url")
    SubElement(url, "loc").text = "/"
    SubElement(url, "priority").text = "1.0"

    # About page
    url = SubElement(urlset, "url")
    SubElement(url, "loc").text = "/about"
    SubElement(url, "priority").text = "0.8"

    # Swagger Docs
    url = SubElement(urlset, "url")
    SubElement(url, "loc").text = "/docs"
    SubElement(url, "priority").text = "0.6"

    # Redoc Docs
    url = SubElement(urlset, "url")
    SubElement(url, "loc").text = "/redoc"
    SubElement(url, "priority").text = "0.6"

    # Universities
    for uni_name in universities.keys():
        url = SubElement(urlset, "url")
        SubElement(url, "loc").text = f"/{uni_name}"
        SubElement(url, "priority").text = "0.9"

    # People
    for person in people:
        url = SubElement(urlset, "url")
        SubElement(url, "loc").text = person.url
        SubElement(url, "priority").text = "0.7"

    return PlainTextResponse(tostring(urlset, encoding="unicode"), media_type="application/xml")


@router.get("/{university}")
def get_university_info(request: Request, university: str):
    with suppress(KeyError):
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

    return RedirectResponse(f"/static/{university}")  # handle static files


@router.get("/{university}/{category}/{name}")
def get_person_info(request: Request, university: Universities, category: Categories, name: Names):
    with suppress(FileNotFoundError):
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
