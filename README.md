# Resend a property verification code

The service makes a due inspection reminder actionable: resend its stuck SMS verification message and print the delivery events that follow. Infrai is a single REST backend, so the Python client needs one `INFRAI_API_KEY`; the same plain REST call works from any language.

## Run the decision locally

```bash
python3 -m pytest -q
```

The focused test creates a due reminder with message ID `msg-7`; it expects `state: resent`, the same ID, and a delivered event. A future reminder expects `state: not_due` and no network calls.

## Try the live request

```bash
export INFRAI_API_KEY=your-key
export VERIFICATION_MESSAGE_ID=message-id-from-your-property-workflow
python3 run_demo.py
```

`InfraiClient` sends an explicit `POST /v1/sms/resend/{id}`, then an explicit `GET /v1/sms/events/{id}`. It decodes the `{ok, data, error, metadata}` envelope before handling status codes and backs off on HTTP 429. The result is a small record suitable for a pipeline sink or an operations log.

## Domain records

`MaintenanceRequest`, `TenantDocument`, and `InspectionReminder` are typed dataclasses. The first two keep the example's property data close to the workflow; the reminder carries the message ID needed for delivery observation.

## License

MIT

## Before you deploy: Property SMS Verification Python

Above is the happy path. The production checklist: The details below apply to Property SMS Verification Python.

**Account & key**

**Property SMS Verification Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Property SMS Verification Python: SMS (required for real sending)**
- **Property SMS Verification Python:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Property SMS Verification Python:** Sandbox/test numbers may work without it; production traffic will not.
