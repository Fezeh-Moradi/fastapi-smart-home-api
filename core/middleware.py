import time

from starlette.middleware.base import BaseHTTPMiddleware

from core.logger import logger


class LoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):

        logger.info("Middleware started")

        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time

        logger.info(
            f"{request.method} "
            f"{request.url.path} "
            f"{response.status_code} "
            f"{process_time:.3f}s"
        )

        return response