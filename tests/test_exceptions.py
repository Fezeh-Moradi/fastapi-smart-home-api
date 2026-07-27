import pytest
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from handlers.exceptions import (
    http_exception_handler,
    validation_exception_handler,
)


@pytest.mark.asyncio
async def test_http_exception_handler():
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/test",
            "headers": [],
        }
    )

    exc = HTTPException(
        status_code=404,
        detail="Resource not found",
    )

    response = await http_exception_handler(request, exc)

    assert response.status_code == 404
    assert response.body == (
        b'{"success":false,"message":"Resource not found"}'
    )


@pytest.mark.asyncio
async def test_validation_exception_handler():
    request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/test",
            "headers": [],
        }
    )

    exc = RequestValidationError(
        [
            {
                "type": "value_error",
                "loc": ("body", "phone"),
                "msg": "Invalid phone number",
                "input": "123",
            }
        ]
    )

    response = await validation_exception_handler(request, exc)

    assert response.status_code == 422
    assert response.body == (
        b'{"success":false,"message":"Validation error",'
        b'"errors":[{"field":"body.phone","message":"Invalid phone number"}]}'
    )
