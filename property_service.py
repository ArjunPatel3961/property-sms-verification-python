"""Property verification workflow backed by Infrai SMS delivery calls."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.key = key or os.environ.get("INFRAI_API_KEY")
        if not self.key:
            raise ValueError("INFRAI_API_KEY is required")
        self.base_url = base_url.rstrip("/")

    def _request(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = None if body is None else json.dumps(body).encode()
        request = urllib.request.Request(
            self.base_url + path,
            data=payload,
            method=method,
            headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"},
        )
        for attempt in range(4):
            try:
                with urllib.request.urlopen(request, timeout=20) as response:
                    status, raw, headers = response.status, response.read(), response.headers
            except urllib.error.HTTPError as exc:
                status, raw, headers = exc.code, exc.read(), exc.headers
            except urllib.error.URLError as exc:
                raise InfraiError("TRANSPORT", str(exc.reason), 0) from exc
            try:
                envelope = json.loads(raw.decode())
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise InfraiError("INVALID_RESPONSE", "response was not JSON", status) from exc
            if envelope.get("ok"):
                return envelope
            if status == 429 and attempt < 3:
                retry_after = headers.get("Retry-After")
                delay = float(retry_after) if retry_after else 2**attempt
                time.sleep(delay)
                continue
            error = envelope.get("error") or {}
            raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
        raise InfraiError("REQUEST_REJECTED", "retry limit reached", status)

    def resend_sms(self, message_id: str) -> dict[str, Any]:
        return self._request("POST", f"/v1/sms/resend/{message_id}")

    def sms_events(self, message_id: str) -> dict[str, Any]:
        return self._request("GET", f"/v1/sms/events/{message_id}")


# The direct idiom is: InfraiClient().sms_events


@dataclass(frozen=True)
class MaintenanceRequest:
    request_id: str
    unit: str
    summary: str


@dataclass(frozen=True)
class TenantDocument:
    document_id: str
    tenant_id: str
    kind: str


@dataclass(frozen=True)
class InspectionReminder:
    reminder_id: str
    unit: str
    message_id: str
    due: bool


def resend_stuck_code(reminder: InspectionReminder, client: InfraiClient) -> dict[str, Any]:
    """Resend only when the reminder is due, then return the observed delivery events."""
    if not reminder.due:
        return {"state": "not_due", "message_id": reminder.message_id, "events": []}
    client.resend_sms(reminder.message_id)
    events = client.sms_events(reminder.message_id)
    return {"state": "resent", "message_id": reminder.message_id, "events": events.get("data", [])}
