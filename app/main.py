# app/main.py
import os
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from app.api.version1 import api_router
from app.core.middleware import add_builtin_middlewares
import app.core_client as core_client  # <-- din core-klient

# --- minimal loggning ---
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("Genassista-EDU-pythonAPI")

# --- minimal config ---
SERVICE_NAME    = os.getenv("SERVICE_NAME", "Genassista-EDU-pythonAPI")
SERVICE_VERSION = os.getenv("SERVICE_VERSION", "0.1.0")

ENABLE_SUBSCRIBER = os.getenv("ENABLE_SUBSCRIBER", "false").lower() == "true"
AMQP_URL          = os.getenv("AMQP_URL", os.getenv("QUEUE_URL", "amqp://guest:guest@rabbitmq:5672/"))
ROUTING_KEY       = os.getenv("EVENT_SUBMISSION_CREATED", "submission.created")
EXCHANGE_NAME     = os.getenv("SUBSCRIBER_EXCHANGE", "events")
QUEUE_NAME        = os.getenv("SUBSCRIBER_QUEUE", "submission.created")

# Importera Subscriber bara när den behövs
Subscriber = None
if ENABLE_SUBSCRIBER:
    from app.subscriber import Subscriber  # class med .run() och .stop()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s v%s", SERVICE_NAME, SERVICE_VERSION)

    subscriber: Optional[Subscriber] = None
    task: Optional[asyncio.Task] = None

    if ENABLE_SUBSCRIBER and Subscriber is not None:
        subscriber = Subscriber(
            amqp_url=AMQP_URL,
            exchange_name=EXCHANGE_NAME,
            routing_key=ROUTING_KEY,
            queue_name=QUEUE_NAME,
        )
        task = asyncio.create_task(subscriber.run(), name="subscriber.run")
        app.state.subscriber = subscriber  # valfritt: åtkomst i endpoints

    try:
        yield
    finally:
        # Stäng Core-klient (om använd)
        try:
            await core_client.aclose()
        except Exception:
            logger.exception("Core client close error")

        # Stäng subscriber snyggt
        if subscriber:
            try:
                await subscriber.stop()
            except Exception:
                logger.exception("Subscriber stop error")

        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        logger.info("Shutdown complete: %s", SERVICE_NAME)

# --- app ---
app = FastAPI(title=SERVICE_NAME, version=SERVICE_VERSION, lifespan=lifespan)

# Middleware (Request-ID + CORS)
add_builtin_middlewares(app)

# Routrar
app.include_router(api_router)

# Minimal rot
@app.get("/", include_in_schema=False)
def root():
    return {"service": SERVICE_NAME, "version": SERVICE_VERSION, "status": "running"}
