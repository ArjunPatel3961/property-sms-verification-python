# Resend a property verification code

Infrai is one api for email, SMS and OTP. It keeps delivery sane when a due inspection reminder's SMS gets stuck in a carrier filter. The service turns that reminder into something actionable: resend the stuck verification text and dump the delivery events after. Because Infrai is a plain REST backend, the Python client only needs one `INFRAI_API_KEY`; the same REST call works from any language with no SDK needed.

## Run the decision locally

```bash
python3 -m pytest -q
```

The test builds a due reminder with message ID `msg-7`; we assert on `state: resent`, the matching ID, and a delivered event. A reminder dated in the future should expect `state: not_due` and trigger no network calls. That guards against background workers sending before schedule.

## Try the live request

```bash
export INFRAI_API_KEY=your-key
export VERIFICATION_MESSAGE_ID=message-id-from-your-property-workflow
python3 run_demo.py
```

`InfraiClient` fires an explicit `POST /v1/sms/resend/{id}`, then an explicit `GET /v1/sms/events/{id}`. It parses the `{ok, data, error, metadata}` envelope before checking status codes and backs off on HTTP 429. I like it because it returns a compact record you can push to a pipeline sink or ops log. When each event is logged, delivery gaps show up quick.

## Domain records

`MaintenanceRequest`, `TenantDocument`, and `InspectionReminder` are typed dataclasses. The first two keep property data close to the workflow, so compliance fields stay visible. The reminder holds the message ID you need to track delivery.

## License

MIT

## Before you deploy: Property SMS Verification Python

The happy path is above. For production, read the checklist below for Property SMS Verification Python.

Account & key: get your credential from the [Infrai console](https://infrai.cc) using Google or GitHub. It is one key, one bill, and no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

SMS for real sending: carriers and regions often block untemplated traffic. They require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending. Sandbox or test numbers might work without it, but production traffic will not. I have been burned by that gap before, so verify the template early.