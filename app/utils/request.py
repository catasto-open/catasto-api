from fastapi import Request
from app.config.logging import create_logger


logger = create_logger(name="app.utils.request")


async def get_real_client(request: Request) -> str:
    ip = None
    for key, value in request.headers.items():
        if key.lower() == "x-real-ip":
            logger.debug(f"Forwarded headers x-real-ip has value {value}")
            ip = value
    if not ip:
        ip = request.client.host
        logger.debug(f"Caller ip is {ip}")
    logger.info(f"Real client ip for access control list is {ip}")
    return ip
