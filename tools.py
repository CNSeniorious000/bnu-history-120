from fastapi import Response, Request
from urllib.parse import unquote
from time import perf_counter_ns
from datetime import datetime
from functools import wraps
from loguru import logger


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
