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
    class GetPersonaByCodiceFiscale(AppExceptionCase):
        def __init__(self, context: Dict[Any, Any]):
            """
            Persona Fisica not found
            """
            status_code = 404
            context = "Persona Fisica not found"
            AppExceptionCase.__init__(self, status_code, context)
    class ImmobileNotFound(AppExceptionCase):
        def __init__(self, context: Dict[Any, Any]):
            """
            Immobile not found
            """
            status_code = 404
            context = "Immobile"
            error = "Not found"
            AppExceptionCase.__init__(self, status_code, error, context)
    class AuthAllowedFqdnError(AppExceptionCase):
        def __init__(self, context: Dict[Any, Any]):
            """
            Authentication of allowed FQDN Error
            """
            status_code = 403
            context = "Server"
            error = "Server name not allowed"
            AppExceptionCase.__init__(self, status_code, error, context)




