"""The REST API (design D7, D9, D12): versioned paths, API tokens, snapshot and events.

There are no writes here (D10).
"""

from __future__ import annotations

import asyncio
import hmac
import json
from collections.abc import AsyncIterator, Mapping, Sequence
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse

from .service import DeviceService, point_json

PREFIX = "/api/v1"
#: Seconds between keep-alive comments on an idle event stream.
KEEPALIVE = 15.0


def sse(event: str, sequence: int, data: Any) -> str:
    """One server-sent event."""
    return f"event: {event}\nid: {sequence}\ndata: {json.dumps(data)}\n\n"


def snapshot_json(service: DeviceService) -> dict[str, Any]:
    poller = service.poller
    points = {} if poller is None else poller.snapshot
    return {
        "device": service.device_id,
        "sequence": service.sequence,
        "points": {key: point_json(state) for key, state in sorted(points.items())},
    }


async def event_stream(service: DeviceService, keepalive: float = KEEPALIVE) -> AsyncIterator[str]:
    """A snapshot first, then one ``change`` event per changed point (D9)."""
    queue = service.subscribe()
    try:
        yield sse("snapshot", service.sequence, snapshot_json(service))
        while True:
            try:
                item = await asyncio.wait_for(queue.get(), timeout=keepalive)
            except TimeoutError:
                yield ": keep-alive\n\n"
                continue
            if item is None:
                return
            sequence, changes = item
            for state in changes:
                yield sse("change", sequence, point_json(state))
    finally:
        service.unsubscribe(queue)


def create_app(
    services: Mapping[str, DeviceService],
    tokens: Sequence[str],
    lifespan: Any = None,
) -> FastAPI:
    """Build the API for ``services``. ``tokens`` are the accepted API tokens."""
    if not tokens or any(not token for token in tokens):
        raise ValueError("at least one non-empty API token is required")

    def require_token(request: Request) -> None:
        header = request.headers.get("authorization", "")
        scheme, _, given = header.partition(" ")
        if scheme.lower() != "bearer" or not any(
            hmac.compare_digest(given.encode(), token.encode()) for token in tokens
        ):
            raise HTTPException(
                status_code=401,
                detail="A valid API token is required",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def get_service(device_id: str) -> DeviceService:
        service = services.get(device_id)
        if service is None:
            raise HTTPException(status_code=404, detail=f"No device {device_id!r}")
        return service

    app = FastAPI(title="modbus-bridge", version="1", lifespan=lifespan)
    auth = [Depends(require_token)]

    @app.get(f"{PREFIX}/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get(f"{PREFIX}/devices", dependencies=auth)
    async def devices() -> list[dict[str, Any]]:
        return [_summary(service) for service in services.values()]

    @app.get(f"{PREFIX}/devices/{{device_id}}", dependencies=auth)
    async def device(device_id: str) -> dict[str, Any]:
        service = get_service(device_id)
        detail = _summary(service)
        if service.device is not None:
            detail["chain"] = [
                {"model_id": m.model_id, "address": m.address, "length": m.length}
                for m in service.device.chain
            ]
        if service.poller is not None:
            found = service.implemented
            detail["not_implemented"] = sorted(found.not_implemented)
            detail["unreadable_models"] = list(found.unreadable_models)
        return detail

    @app.get(f"{PREFIX}/devices/{{device_id}}/points", dependencies=auth)
    async def points(device_id: str) -> dict[str, Any]:
        return snapshot_json(get_service(device_id))

    @app.get(f"{PREFIX}/devices/{{device_id}}/quirks", dependencies=auth)
    async def quirks(device_id: str) -> dict[str, Any]:
        service = get_service(device_id)
        if service.quirks is None:
            raise HTTPException(status_code=503, detail=f"Device {device_id!r} is not ready")
        return {"device": service.device_id, **service.quirks.report()}

    @app.get(f"{PREFIX}/devices/{{device_id}}/events", dependencies=auth)
    async def events(device_id: str) -> StreamingResponse:
        service = get_service(device_id)
        return StreamingResponse(
            event_stream(service),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache"},
        )

    return app


def _summary(service: DeviceService) -> dict[str, Any]:
    summary: dict[str, Any] = {"id": service.device_id, "ready": service.poller is not None}
    if service.device is not None:
        ident = service.device.identity
        summary["identity"] = {
            "manufacturer": ident.manufacturer,
            "model": ident.model,
            "options": ident.options,
            "version": ident.version,
            "serial": ident.serial,
            "device_address": ident.device_address,
        }
    if service.poller is not None:
        summary["implemented_points"] = len(service.implemented.implemented)
        summary["implemented_source"] = service.implemented.source
        summary["last_error"] = service.poller.last_error
    return summary
