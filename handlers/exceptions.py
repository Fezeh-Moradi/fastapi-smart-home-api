from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

async def http_exception_handler(
        request: Request,
        exc: HTTPException
):
    
    return JSONResponse(
        status_code= exc.status_code,
        content={
            "success": False,
            "message": exc.detail
        }
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):

    errors = [
        {
            "field": ".".join(map(str, error["loc"])),
            "message": error["msg"],
        }
        for error in exc.errors()
    ]

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation error",
            "errors": errors
        }
    )
    
 