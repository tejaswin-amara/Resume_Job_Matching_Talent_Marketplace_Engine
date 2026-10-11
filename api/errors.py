import uuid

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
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
            "instance": f"urn:uuid:{uuid.uuid4()}",
        },
        headers={"Content-Type": "application/problem+json"},
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": "about:blank",
            "title": "HTTP Error",
            "status": exc.status_code,
            "detail": str(exc.detail),
            "instance": f"urn:uuid:{uuid.uuid4()}",
        },
        headers={"Content-Type": "application/problem+json"},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "type": "about:blank",
            "title": "Validation Error",
            "status": 422,
            "detail": str(exc.errors()),
            "instance": f"urn:uuid:{uuid.uuid4()}",
        },
        headers={"Content-Type": "application/problem+json"},
    )


async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "type": "about:blank",
            "title": "Internal Server Error",
            "status": 500,
            "detail": "An unexpected error occurred.",
            "instance": f"urn:uuid:{uuid.uuid4()}",
        },
        headers={"Content-Type": "application/problem+json"},
    )
