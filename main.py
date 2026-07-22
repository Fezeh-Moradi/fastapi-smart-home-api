from fastapi import FastAPI,HTTPException
from fastapi.exceptions import RequestValidationError
from handlers.exceptions import http_exception_handler, validation_exception_handler
from routers import auth, users, devices
from core.logger import logger
from core.middleware import LoggingMiddleware

app = FastAPI()

print("Server IS RUNNING")

app.add_middleware(LoggingMiddleware)

logger.info("Application started")

app.add_exception_handler(
    HTTPException,
    http_exception_handler
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(devices.router)


@app.get("/")
def root():
    return {
        "message": "Smart Home API is running"
    }


