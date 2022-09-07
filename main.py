from brotli_asgi import BrotliMiddleware
from traceback import format_exc
from fastapi.responses import *
from fastapi import FastAPI
from hashlib import md5
from enum import Enum
from person import *

app = FastAPI(title="BNU 120 years 🎉", description=open("readme.md", encoding="utf-8").read(), version="dev")
app.add_middleware(BrotliMiddleware, quality=11)


class Universities(Enum):
    BNU = "北师大"
    FuJen = "辅大"
    BFHNC = "女高师"


@app.get("/{university}", responses={200: {"content": {"text/html": {}}}})
def get_university_info(university: Universities):
    try:
        html = University(university.value, []).html
        response = HTMLResponse(html)
        response.headers["ETag"] = f'W/"{md5(html.encode("utf-8")).hexdigest()}"'
        return response
    except NotADirectoryError:
        return ORJSONResponse(format_exc(chain=False), 422)
