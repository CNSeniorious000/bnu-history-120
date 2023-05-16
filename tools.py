from fastapi import Response, Request
from person import University
from functools import wraps
from hashlib import md5
import env


def get_etag(response: Response):
    return f'W/"{md5(response.body).hexdigest()}"'


def add_etag(response: Response):
    response.headers["ETag"] = get_etag(response)
    return response


def cache_with_etag(handler):
    assert callable(handler)

    @wraps(handler)
    def inner(request: Request, *args, **kwargs):
        etag = request.headers.get("If-None-Match")
        response: Response = handler(request, *args, **kwargs)
        if response.status_code // 100 == 2:
            if (new_etag := get_etag(response)) == etag:
                return Response(None, 304)
            else:
                response.headers["ETag"] = new_etag
        return response

    return inner


def make_shared_context(request: Request):
    return {"env": env, "universities": University.universities}
