from typing import Any, Dict

from fastapi import Request
from starlette.responses import JSONResponse


class AppExceptionCase(Exception):
    def __init__(self, status_code: int, error: str, context: dict):
        self.exception_case = self.__class__.__name__
        self.status_code = status_code
        self.error = error
        self.context = context

    def __str__(self):
        return (
            f"<AppException {self.exception_case} - error={self.error}"
            + f"status_code={self.status_code} - context={self.context}>"
        )


async def app_exception_handler(request: Request, exc: AppExceptionCase):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error,
            "context": exc.context,
        },
    )


class AppException:
    class ShapefileNotValid(AppExceptionCase):
        def __init__(self, context: Dict[Any, Any]):
            """
            Shapefile is not valid
            """
            status_code = 422
            error = "The dataset is not a valid Shapefile"
            AppExceptionCase.__init__(self, status_code, error, context)

    class GeopackageNotValid(AppExceptionCase):
        def __init__(self, context: Dict[Any, Any]):
            """
            Geopackage is not valid
            """
            status_code = 422
            error = "The dataset is not a valid Geopackage"
            AppExceptionCase.__init__(self, status_code, error, context)
