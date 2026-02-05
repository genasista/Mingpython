"""RabbitMQ-based subscriber using aio-pika.

Durable queue with manual acks, simple reconnect and backoff, and offline replay
via durable queue persistence.
"""
import os
import json
import asyncio
import logging
import aio_pika
from aio_pika.abc import AbstractIncomingMessage

logger = logging.getLogger("Genassista-EDU-pythonAPI.subscriber")

# --- env with sensible defaults ---
AMQP_URL          = os.getenv("AMQP_URL", os.getenv("QUEUE_URL", "amqp://guest:guest@rabbitmq:5672/"))
EXCHANGE_NAME     = os.getenv("SUBSCRIBER_EXCHANGE", "events")
ROUTING_KEY       = os.getenv("SUBSCRIBER_ROUTING_KEY", os.getenv("EVENT_SUBMISSION_CREATED", "submission.created"))
QUEUE_NAME        = os.getenv("SUBSCRIBER_QUEUE", "submission.created")
PREFETCH_COUNT    = int(os.getenv("SUBSCRIBER_BATCH_SIZE", "10"))
STARTUP_RETRY_SEC = float(os.getenv("SUBSCRIBER_STARTUP_RETRY_SEC", "1.0"))
BACKOFF_ON_FAIL   = float(os.getenv("SUBSCRIBER_BACKOFF_ON_FAIL", "1.0"))


class Subscriber:
    def __init__(self, amqp_url: str | None = None, exchange_name: str | None = None, routing_key: str | None = None, queue_name: str | None = None):
        self.amqp_url = amqp_url or AMQP_URL
        self.exchange_name = exchange_name or EXCHANGE_NAME
        self.routing_key = routing_key or ROUTING_KEY
        self.queue_name = queue_name or QUEUE_NAME
        self._stopping = asyncio.Event()
        self.is_connected: bool = False
        self._connection: aio_pika.RobustConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None
        self._queue: aio_pika.abc.AbstractQueue | None = None
        self._exchange: aio_pika.abc.AbstractExchange | None = None

    async def _connect(self) -> None:
        while not self._stopping.is_set():
            try:
                self._connection = await aio_pika.connect_robust(self.amqp_url)
                self._channel = await self._connection.channel()
                await self._channel.set_qos(prefetch_count=PREFETCH_COUNT)

                self._exchange = await self._channel.declare_exchange(
                    self.exchange_name,
                    aio_pika.ExchangeType.TOPIC,
                    durable=True,
                )
                self._queue = await self._channel.declare_queue(
                    self.queue_name,
                    durable=True,
                )
                await self._queue.bind(self._exchange, routing_key=self.routing_key)

                self.is_connected = True
                logger.info(
                    "Connected to RabbitMQ: %s exchange=%s queue=%s routing_key=%s",
                    self.amqp_url, self.exchange_name, self.queue_name, self.routing_key,
                )
                return
            except Exception as e:
                self.is_connected = False
                logger.warning("RabbitMQ connect failed: %s — retry in %.1fs", e, STARTUP_RETRY_SEC)
                await asyncio.sleep(STARTUP_RETRY_SEC)

    async def handle(self, payload: dict) -> bool:
        # Minimal “process submission”: simulate OK
        return True

    async def _process_message(self, message: AbstractIncomingMessage) -> None:
        async with message.process(requeue=False):
            try:
                body = message.body.decode("utf-8", "ignore")
                try:
                    payload = json.loads(body)
                except Exception:
                    payload = {"raw": body}

                headers = message.headers or {}
                corr = headers.get("x-correlation-id") or headers.get("X-Correlation-Id")
                event_id = headers.get("x-event-id") or headers.get("X-Event-Id") or payload.get("eventId")

                submission_id = (
                    payload.get("submissionId")
                    or payload.get("id")
                    or payload.get("submission_id")
                )

                ok = False
                try:
                    ok = await self.handle(payload)
                except Exception as e:
                    logger.warning("handler error: %s", e)

                if ok:
                    logger.info(
                        "received submissionId=%s eventId=%s correlationId=%s acked",
                        submission_id, event_id, corr,
                    )
                else:
                    # Raise to trigger nack and requeue based on policy
                    logger.warning(
                        "processing failed submissionId=%s eventId=%s correlationId=%s retrying",
                        submission_id, event_id, corr,
                    )
                    # Sleep a bit to back off; message will be re-delivered later
                    await asyncio.sleep(BACKOFF_ON_FAIL)
                    raise RuntimeError("processing failed")

            except Exception:
                # By exiting context manager with exception, message remains unacked; we can explicitly nack
                try:
                    await message.nack(requeue=True)
                except Exception:
                    pass

    async def run(self) -> None:
        try:
            await self._connect()
            if not self.is_connected:
                return

            assert self._queue is not None
            # Consume with manual ack (handled by context manager above)
            async with self._queue.iterator(timeout=1.0) as queue_iter:
                async for message in queue_iter:
                    if self._stopping.is_set():
                        break
                    await self._process_message(message)
        except asyncio.TimeoutError:
            # normal idle timeout; loop again if not stopping
            if not self._stopping.is_set():
                await self.run()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.exception("Subscriber crashed: %s", e)
        finally:
            self.is_connected = False
            try:
                if self._channel is not None and not self._channel.is_closed:
                    await self._channel.close()
            except Exception:
                logger.exception("Error during channel close")
            try:
                if self._connection is not None and not self._connection.is_closed:
                    await self._connection.close()
            except Exception:
                logger.exception("Error during connection close")
            logger.info("Subscriber stopped")

    async def stop(self) -> None:
        self._stopping.set()
