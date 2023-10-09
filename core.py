from datetime import datetime
from hashlib import md5
from os import environ
from pathlib import Path
from time import perf_counter_ns
from urllib.parse import unquote

from brotli_asgi import BrotliMiddleware
from fastapi import FastAPI, Request, Response
from fastapi.responses import ORJSONResponse, PlainTextResponse, RedirectResponse, StreamingResponse
from loguru import logger
from rcssmin import cssmin
from rjsmin import jsmin
from starlette.templating import Jinja2Templates

from person import universities

STATIC = Path("./static/")


def make_shared_context(_):
    return {"env": environ, "universities": universities.values()}


app = FastAPI(
    title="BNU 120 years 🎉",
    description=open("readme.md", encoding="utf-8").read(),
    version="dev",
    contact={
        "name": "Muspi Merol",
        "url": "https://muspimerol.site/",
        "email": "admin@muspimerol.site",
    },
    default_response_class=ORJSONResponse,
)


@app.middleware("http")
async def negotiated_cache(request: Request, call_next):
    if request.method not in {"GET", "HEAD"}:
        return await call_next(request)
    etag = request.headers.get("If-None-Match")
    response: StreamingResponse = await call_next(request)
    if response.status_code // 100 != 2:
        return response

    body = b"".join([part async for part in response.body_iterator])

    if (new_etag := f'W/"{md5(body).hexdigest()}"') == etag:
        return Response(None, 304)

    return Response(
        body,
        response.status_code,
        {"Etag": new_etag, **response.headers},
        response.media_type,
    )


app.add_middleware(BrotliMiddleware, quality=11)


@app.middleware("http")
async def fine_log(request: Request, call_next):
    now = datetime.now()
    t = perf_counter_ns()
    response: Response = await call_next(request)
    log = {2: logger.debug, 3: logger.success, 4: logger.error, 5: logger.critical}[
        response.status_code // 100
    ]
    log(
        " ".join(
            (
                f"[{response.status_code}]",
                f"{now.month}月{now.day}日 {now.hour}:{now.minute}:{now.second}",
                f"in {(perf_counter_ns() - t) // 1_000_000}ms",
                f"to {unquote(str(request.url))}",
            )
        )
    )

    return response


template = Jinja2Templates("./templates", context_processors=[make_shared_context])
TemplateResponse = template.TemplateResponse


@app.get("/favicon.ico", include_in_schema=False)
def get_favicon_ico():
    return RedirectResponse("/static/icon/favicon.ico")


@app.get("/robots.txt", include_in_schema=False)
def on_scraper(request: Request):
    print(request.headers.get("user-agent"))
    return PlainTextResponse("User-agent: *\nAllow: /")


@app.get("/{filename}.css", include_in_schema=False)
def render_css(filename: str):
    css = STATIC / f"{filename}.css"
    if not css.is_file():
        return PlainTextResponse(f"{css} is not a file", 404)

    css_light = STATIC / f"{filename}-light.css"
    css_dark = STATIC / f"{filename}-dark.css"

    if css_light.is_file() and css_dark.is_file():
        # generate mixed style sheet
        return Response(
            cssmin(
                "\n".join(
                    (
                        css.read_text("utf-8"),
                        "@media (prefers-color-scheme: light) {",
                        css_light.read_text("utf-8"),
                        "}",
                        "@media (prefers-color-scheme: dark) {",
                        css_dark.read_text("utf-8"),
                        "}",
                    )
                )
            ),
            media_type="text/css",
        )

    return Response(cssmin(css.read_text("utf-8")), media_type="text/css")


@app.get("/sw.js", include_in_schema=False)
def get_service_worker():
    return get_compressed_javascript("static/sw")


@app.get("/{filename:path}.js", include_in_schema=False)
def get_compressed_javascript(filename: str):
    return Response(
        jsmin(Path(f"./{filename}.js").read_text("utf-8")), media_type="application/javascript"
    )
