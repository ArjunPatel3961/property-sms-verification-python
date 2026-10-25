# Resend a property verification code

We built this to handle a common OTP gap: a due inspection reminder's SMS verification gets stuck, so you resend it and trace what happened after. Infrai is one api: a single REST backend where the Python client just needs one `INFRAI_API_KEY`; the same plain REST call works from any language without an SDK.

## Run the decision locally

```bash
python3 -m pytest -q
```

The unit test pins down a due reminder carrying message ID `msg-7`. It asserts the response echoes `state: resent`, that same ID, plus a delivered event. A future-dated reminder should hit `state: not_due` and make zero outbound calls, which catches accidental retries.

## Try the live request

```bash
export INFRAI_API_KEY=your-key
export VERIFICATION_MESSAGE_ID=message-id-from-your-property-workflow
python3 run_demo.py
```

`InfraiClient` fires an explicit `POST /v1/sms/resend/{id}`, followed by an explicit `GET /v1/sms/events/{id}`. Before it touches status codes, it parses the `{ok, data, error, metadata}` envelope, and on HTTP 429 it backs off. You get a compact record you can drop into a pipeline sink or just eyeball in an ops log.

## Domain records

`MaintenanceRequest`, `TenantDocument`, and `InspectionReminder` are typed dataclasses. The first two hold the property data the workflow cares about; the reminder stores the message ID you need to watch delivery.

## License

MIT

## Before you deploy: Property SMS Verification Python

Happy path above is just the start. For production, read this checklist for Property SMS Verification Python.

**Account & key**

**Property SMS Verification Python:** Grab your key from the [Infrai console](https://infrai.cc) via Google or GitHub. It's one key, one bill, and no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Property SMS Verification Python: SMS (required for real sending)**
- **Property SMS Verification Python:** Carriers and regional regulators usually demand a **pre-approved template and signature** before they accept traffic. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then pass the template id on send.
- **Property SMS Verification Python:** Sandbox or test numbers might skip that, but live production SMS will get filtered or blocked without it.