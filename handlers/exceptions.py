from fastapi import Request, HTTPException
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
    
    errors = []

    for error in exc.errors():
        errors.append(
            {
                "field": ".".join(map(str, error["loc"])),
                "message": error["msg"]
            }
        )

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation Error",
            "errors": errors
        }
    )
    
 