from fastapi import Request
from markdown2 import markdown_path
from starlette.staticfiles import StaticFiles

from api import router as api
from core import TemplateResponse, app
from pages import router as pages
from person import markdown_extensions


@app.get("/about", include_in_schema=False)
def about_page(request: Request):
    return TemplateResponse(
        "person.jinja2",
        {
            "request": request,
            "non_spa": True,
            "title": "🏗 under construction",
            "name": "readme.md",
            "markdown": markdown_path("./readme.md", extras=markdown_extensions),
        },
    )


@app.get("/", include_in_schema=False)
def home_page(request: Request):
    return TemplateResponse("index.jinja2", {"request": request})


app.mount("/static/", StaticFiles(directory="./static/"))
app.include_router(api)
app.include_router(pages)
