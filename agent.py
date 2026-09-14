"""Veille Back-office Concierge — an autonomous Strands agent.

Runs on a schedule (or on demand). Reviews the last 24h of after-hours calls and
bookings, drafts confirmations for the clear ones, catches scheduling conflicts
and ambiguities, and surfaces ONLY the items a human must decide as staff tasks.
"""
import os

from dotenv import load_dotenv
from strands import Agent
from strands.models import BedrockModel

import tools

load_dotenv()

SYSTEM_PROMPT = """You are Veille's autonomous back-office concierge for a small
business that uses an after-hours AI receptionist. Once per run you clear the
routine follow-up so the owner doesn't have to, and you only surface decisions a
human must make.

Do this, using your tools:
1. Call list_recent_bookings and list_recent_calls (last 24 hours).
2. For each clear, unambiguous booking (has a name, a service, and a future
   confirmed time), draft a confirmation with draft_confirmation_text.
3. Call find_double_bookings. For every conflict, create ONE staff task
   (severity 'review') that names both customers, the clashing time, and a
   recommended fix.
4. Create a staff task for anything ambiguous or unresolved: a booking missing a
   service or time, or a call whose status is still 'escalated'/urgent and
   unhandled. Use severity 'urgent' for genuinely urgent items.

Rules:
- Do NOT send anything to customers. Confirmations are drafts for a human.
- Only create staff tasks for things that need a human decision — do not create
  tasks for routine bookings you were able to handle.
- Finish with a short plain-text report: how many bookings reviewed, how many
  confirmations drafted, and how many staff tasks you created and why.
"""


def build_agent() -> Agent:
    model = BedrockModel(
        model_id=os.environ.get("BEDROCK_MODEL_ID", "us.amazon.nova-lite-v1:0"),
        region_name=os.environ.get("AWS_REGION", "us-east-2"),
    )
    return Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[
            tools.list_recent_bookings,
            tools.list_recent_calls,
            tools.find_double_bookings,
            tools.draft_confirmation_text,
            tools.create_staff_task,
        ],
    )


def main() -> None:
    agent = build_agent()
    result = agent("Run the daily back-office review now.")
    print("\n=== Concierge report ===\n")
    print(result)


if __name__ == "__main__":
    main()
