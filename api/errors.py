from fastapi import Request
from fastapi.responses import JSONResponse


class ProblemDetailException(Exception):
    def __init__(self, status: int, title: str, detail: str, type_uri: str = "about:blank"):
        self.status = status
        self.title = title
        self.detail = detail
        self.type_uri = type_uri


async def problem_detail_handler(request: Request, exc: ProblemDetailException):
    return JSONResponse(
        status_code=exc.status,
        content={
            "type": exc.type_uri,
            "title": exc.title,
            "status": exc.status,
            "detail": exc.detail,
        },
        headers={"Content-Type": "application/problem+json"},
    )
