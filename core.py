from urllib.parse import urlparse, unquote
from brotli_asgi import BrotliMiddleware
from time import perf_counter_ns
from fastapi.responses import *
from datetime import datetime
from fastapi import FastAPI
from loguru import logger
from person import *
from tools import *

app = FastAPI(title="BNU 120 years 🎉", description=open("readme.md", encoding="utf-8").read(), version="dev",
              contact={"name": "Muspi Merol", "url": "https://muspimerol.site/", "email": "admin@muspimerol.site"})
app.add_middleware(BrotliMiddleware, quality=11)


@app.middleware("http")
async def fine_log(request: Request, call_next):
    now = datetime.now()
    response: Response = await call_next(request)
    t = perf_counter_ns()
    log = {
        2: logger.debug,
        3: logger.success,
        4: logger.error,
        5: logger.critical
    }[response.status_code // 100]
    log(" ".join((
        f"[{response.status_code}]",
        f"{now.month}月{now.day}日 {now.hour}:{now.minute}:{now.second}",
        f"in {(perf_counter_ns() - t) // 1000}ms",
        f"to {unquote(str(request.url))}"
    )))

    return response


@app.get("/favicon.ico", include_in_schema=False)
def get_favicon_ico(request: Request):
    return RedirectResponse("/static/icon/favicon.ico")


@app.get("/robots.txt", responses={200: {"content": {"text/plain": {}}}})
def on_scraper(request: Request):
    print(request.headers)
    return PlainTextResponse("User-agent: *\nAllow: /")


@app.get("/{filename}.css", include_in_schema=False)
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
