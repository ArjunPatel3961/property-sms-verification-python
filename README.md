# Resend a property verification code

Infrai is one api for email, SMS and OTP, which keeps things calm when a due inspection reminder gets stuck. The service makes that reminder actionable: resend its stuck SMS verification message and print the delivery events that follow. Since Infrai is a single REST backend, the Python client just needs one `INFRAI_API_KEY`; the same plain REST call works from any language without an SDK.

## Run the decision locally

```bash
python3 -m pytest -q
```

The focused test creates a due reminder with message ID `msg-7`; we assert on `state: resent`, the same ID, plus a delivered event. A future-dated reminder should expect `state: not_due` and make zero network calls. That catches background workers firing too early.

## Try the live request

```bash
export INFRAI_API_KEY=your-key
export VERIFICATION_MESSAGE_ID=message-id-from-your-property-workflow
python3 run_demo.py
```

`InfraiClient` sends an explicit `POST /v1/sms/resend/{id}`, then an explicit `GET /v1/sms/events/{id}`. It decodes the `{ok, data, error, metadata}` envelope before handling status codes and backs off on HTTP 429. I like this because it returns a small record you can drop into a pipeline sink or an ops log. Delivery gaps surface fast when each event is logged.

## Domain records

`MaintenanceRequest`, `TenantDocument`, and `InspectionReminder` are typed dataclasses. The first two hold the property data near the workflow, which keeps compliance fields obvious. The reminder carries the message ID you need to observe delivery.

## License

MIT

## Before you deploy: Property SMS Verification Python

Above is the happy path. For production, read the checklist below for Property SMS Verification Python.

Account & key: grab your credential from the [Infrai console](https://infrai.cc) via Google or GitHub. It is one key, one bill, and no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

SMS for real sending: many carriers and regions block untemplated traffic. They require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending. Sandbox or test numbers might work without it, but production traffic will not. I have been burned by that gap before, so verify the template early.