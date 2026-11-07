"""The REST API (design D7, D9, D12): versioned paths, API tokens, snapshot and events.

There are no writes to devices here (D10). The user's own quirks (design 2b) are
created, checked, previewed, removed and switched off here. Each change is added
to the device's audit log with the token that made it (U5, U8).

A read-only page is served at ``/ui`` (P2U). It holds no data and reads everything
through the token-protected API.
"""

from __future__ import annotations

import asyncio
import hmac
import json
from collections.abc import AsyncIterator, Mapping, Sequence
from importlib.resources import files
from typing import Annotated, Any

from fastapi import Body, Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse

from .quirks import QuirkError
from .service import (
    AuditError,
    DeviceChanged,
    DeviceService,
    UserQuirksOff,
    identity_json,
    point_json,
)
from .user_quirks import check_kind

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
    """A snapshot first, then a ``change`` event per changed point and a ``removed``
    event per point a quirk took away (D9). A ``device`` event gives the new identity
    when the same device is found with other firmware or options after a reconnect."""
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
            if isinstance(item, DeviceChanged):
                yield sse("device", service.sequence, {"identity": item.identity})
                continue
            sequence, changes, removed = item
            for state in changes:
                yield sse("change", sequence, point_json(state))
            for key in removed:
                yield sse("removed", sequence, {"key": key})
    finally:
        service.unsubscribe(queue)


def require_token(request: Request) -> str:
    """Who is calling: ``token N``, N being the token's place in the list from 1."""
    tokens: Sequence[str] = request.app.state.tokens
    header = request.headers.get("authorization", "")
    scheme, _, given = header.partition(" ")
    matches = [hmac.compare_digest(given.encode(), token.encode()) for token in tokens]
    if scheme.lower() != "bearer" or not any(matches):
        raise HTTPException(
            status_code=401,
            detail="A valid API token is required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return f"token {matches.index(True) + 1}"


#: The caller of an endpoint, as logged in the audit log.
Who = Annotated[str, Depends(require_token)]


def create_app(
    services: Mapping[str, DeviceService],
    tokens: Sequence[str],
    lifespan: Any = None,
) -> FastAPI:
    """Build the API for ``services``. ``tokens`` are the accepted API tokens."""
    if not tokens or any(not token for token in tokens):
        raise ValueError("at least one non-empty API token is required")

    def get_service(device_id: str) -> DeviceService:
        service = services.get(device_id)
        if service is None:
            raise HTTPException(status_code=404, detail=f"No device {device_id!r}")
        return service

    app = FastAPI(title="modbus-bridge", version="1", lifespan=lifespan)
    app.state.tokens = list(tokens)
    auth = [Depends(require_token)]

    @app.get("/ui", include_in_schema=False)
    async def ui() -> HTMLResponse:
        page = files("modbus_bridge").joinpath("ui/index.html").read_text(encoding="utf-8")
        return HTMLResponse(page, headers={"Cache-Control": "no-cache"})

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

    def ready(device_id: str) -> DeviceService:
        service = get_service(device_id)
        if service.quirks is None:
            raise HTTPException(status_code=503, detail=f"Device {device_id!r} is not ready")
        return service

    async def edit(call: Any) -> Any:
        """Run a user-quirk change, turning its refusals into HTTP answers."""
        try:
            return await call
        except UserQuirksOff as err:
            raise HTTPException(status_code=409, detail=str(err)) from err
        except AuditError as err:
            raise HTTPException(status_code=500, detail=str(err)) from err
        except QuirkError as err:
            raise HTTPException(status_code=422, detail=str(err)) from err

    user_path = f"{PREFIX}/devices/{{device_id}}/user-quirks"

    @app.get(user_path, dependencies=auth)
    async def user_quirks(device_id: str) -> dict[str, Any]:
        return ready(device_id).user_json()

    @app.post(f"{user_path}/check", dependencies=auth)
    async def check_user_quirk(device_id: str, body: Annotated[Any, Body()]) -> dict[str, Any]:
        if not isinstance(body, dict) or set(body) != {"kind", "item"}:
            raise HTTPException(status_code=422, detail="body must be {kind, item}")
        service = ready(device_id)
        _, _, preview = await edit(service.check_user_item(body["kind"], body["item"]))
        return preview

    def read(call: Any) -> Any:
        """Read the user quirks' log, turning its errors into HTTP answers."""
        try:
            return call()
        except UserQuirksOff as err:
            raise HTTPException(status_code=409, detail=str(err)) from err
        except QuirkError as err:
            raise HTTPException(status_code=500, detail=str(err)) from err

    @app.get(f"{user_path}/audit", dependencies=auth)
    async def audit(device_id: str, id: str | None = None) -> dict[str, Any]:
        service = ready(device_id)
        return read(lambda: service.audit_json(id))

    @app.get(f"{user_path}/{{kind}}/{{item_id}}/versions", dependencies=auth)
    async def versions(device_id: str, kind: str, item_id: str) -> dict[str, Any]:
        service = ready(device_id)
        try:
            check_kind(kind)
        except QuirkError as err:
            raise HTTPException(status_code=422, detail=str(err)) from err
        return read(lambda: service.versions_json(kind, item_id))

    @app.get(f"{user_path}/{{kind}}/{{item_id}}/export", dependencies=auth)
    async def export(device_id: str, kind: str, item_id: str) -> dict[str, Any]:
        service = ready(device_id)
        try:
            return service.export_json(kind, item_id)
        except UserQuirksOff as err:
            raise HTTPException(status_code=409, detail=str(err)) from err
        except AuditError as err:
            raise HTTPException(status_code=500, detail=str(err)) from err
        except KeyError as err:
            raise HTTPException(status_code=404, detail=f"No user {kind} {item_id!r}") from err
        except QuirkError as err:
            raise HTTPException(status_code=422, detail=str(err)) from err

    @app.put(f"{user_path}/{{kind}}/{{item_id}}")
    async def save_user_quirk(
        device_id: str, kind: str, item_id: str, item: Annotated[Any, Body()], who: Who
    ) -> dict[str, Any]:
        if not isinstance(item, dict) or item.get("id") != item_id:
            raise HTTPException(status_code=422, detail="the item's id must match the path")
        return await edit(ready(device_id).save_user_item(kind, item, who))

    @app.delete(f"{user_path}/{{kind}}/{{item_id}}")
    async def remove_user_quirk(
        device_id: str, kind: str, item_id: str, who: Who, reason: str | None = None
    ) -> dict[str, Any]:
        try:
            warnings = await edit(ready(device_id).remove_user_item(kind, item_id, who, reason))
        except KeyError as err:
            raise HTTPException(status_code=404, detail=f"No user {kind} {item_id!r}") from err
        return {"removed": item_id, "warnings": warnings}

    @app.put(f"{PREFIX}/devices/{{device_id}}/quirks/{{item_id}}/off")
    async def switch_off(
        device_id: str, item_id: str, who: Who, reason: str | None = None
    ) -> dict[str, Any]:
        warnings = await edit(ready(device_id).switch_off(item_id, True, who, reason))
        return {"id": item_id, "off": True, "warnings": warnings}

    @app.delete(f"{PREFIX}/devices/{{device_id}}/quirks/{{item_id}}/off")
    async def switch_on(
        device_id: str, item_id: str, who: Who, reason: str | None = None
    ) -> dict[str, Any]:
        warnings = await edit(ready(device_id).switch_off(item_id, False, who, reason))
        return {"id": item_id, "off": False, "warnings": warnings}

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
    summary: dict[str, Any] = {
        "id": service.device_id,
        "ready": service.poller is not None,
        "interval": service.interval,
    }
    if service.device is not None:
        summary["identity"] = identity_json(service.device.identity)
    if service.poller is not None:
        summary["implemented_points"] = len(service.implemented.implemented)
        summary["implemented_source"] = service.implemented.source
        summary["last_error"] = service.poller.last_error
    summary["refused"] = service.refused
    return summary
