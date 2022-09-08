from fastapi import Response, Request
from urllib.parse import unquote
from time import perf_counter_ns
from datetime import datetime
from functools import wraps
from loguru import logger
from hashlib import md5


def get_etag(response: Response):
    return f'W/"{md5(response.body).hexdigest()}"'


def add_etag(response: Response):
    response.headers["ETag"] = get_etag(response)
    return response


def fine_log(handler):
    assert callable(handler)

    @wraps(handler)
    def inner(request: Request, *args, **kwargs):
        now = datetime.now()
        response: Response = handler(request, *args, **kwargs)

        t = perf_counter_ns()
        match response.status_code // 100:
            case 2:
                log = logger.success
            case 3:
                log = logger.info
            case 4:
                log = logger.warning
            case 5:
                log = logger.error
            case _:
                log = logger.critical

        log(" ".join((
            f"[{response.status_code}]",
            f"{now.month}月{now.day}日 {now.hour}:{now.minute}:{now.second}",
            f"in {(perf_counter_ns() - t) // 1000}ms",
            f"to {unquote(str(request.url))}"
        )))

        return response

    return inner


def cache_with_etag(handler):
    assert callable(handler)

    @wraps(handler)
    def inner(request: Request, *args, **kwargs):
        etag = request.headers.get("If-Match")
        response: Response = handler(request, *args, **kwargs)
        if response.status_code // 100 == 2:
            if (new_etag := get_etag(response)) == etag:
                return Response(None, 304)
            else:
                response.headers["ETag"] = new_etag
        return response

    return inner
