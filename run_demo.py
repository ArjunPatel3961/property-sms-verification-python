import json
import os

from property_service import InfraiClient, InspectionReminder, resend_stuck_code


if __name__ == "__main__":
    if not os.environ.get("INFRAI_API_KEY"):
        raise SystemExit("Set INFRAI_API_KEY before running the demo")
    reminder = InspectionReminder("inspection-42", "B-204", os.environ["VERIFICATION_MESSAGE_ID"], True)
    print(json.dumps(resend_stuck_code(reminder, InfraiClient()), indent=2))

