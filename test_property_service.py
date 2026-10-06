from property_service import InspectionReminder, resend_stuck_code


class RecordingClient:
    def __init__(self):
        self.calls = []

    def resend_sms(self, message_id):
        self.calls.append(("resend", message_id))
        return {"ok": True}

    def sms_events(self, message_id):
        self.calls.append(("events", message_id))
        return {"ok": True, "data": [{"status": "delivered"}]}


def test_due_reminder_resends_and_surfaces_delivery_state():
    client = RecordingClient()
    result = resend_stuck_code(InspectionReminder("r-7", "A-12", "msg-7", True), client)
    assert result == {"state": "resent", "message_id": "msg-7", "events": [{"status": "delivered"}]}
    assert client.calls == [("resend", "msg-7"), ("events", "msg-7")]


def test_future_reminder_does_not_send():
    client = RecordingClient()
    result = resend_stuck_code(InspectionReminder("r-8", "A-12", "msg-8", False), client)
    assert result["state"] == "not_due"
    assert client.calls == []

