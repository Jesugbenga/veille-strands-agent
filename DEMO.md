# 5-Minute Demo Script — Veille Back-office Concierge

An autonomous **Strands agent** on **Amazon Bedrock** that clears a small
business's overnight follow-up and surfaces only the decisions a human must make.

## Setup (before recording)
```bash
pip install -r requirements.txt
cp .env.example .env         # fill Supabase + AWS values; set BEDROCK_MODEL_ID=us.amazon.nova-lite-v1:0
aws configure                # IAM user with AmazonBedrockFullAccess, region us-east-2
python seed_demo.py          # creates a double-booking, a missing-service booking, an urgent call
```
Have the Veille dashboard (**app.veille.biz**) open on the overview page.

## Script

### 0:00–0:40 — The problem
> "After hours, small businesses miss calls and wake up to a pile of overnight
> follow-up. Veille already answers the calls and books appointments — but a
> human still has to review every booking each morning: confirm the clear ones,
> catch double-bookings, chase the ambiguous ones. That's repetitive,
> judgment-heavy busywork."

### 0:40–1:10 — Who it's for & what it is
> "Meet the Veille Back-office Concierge — an autonomous agent built with the
> **AWS Strands Agents SDK**, running on **Amazon Bedrock (Nova)**. It's for
> small-business owners. It runs quietly in the background and only pings when
> there's a real decision to make."

### 1:10–3:30 — Live demo
1. Show the seeded mess (Supabase `bookings`, or the dashboard calendar): two
   overlapping appointments, one with no service, plus an urgent escalated call.
2. Run it:
   ```bash
   python agent.py
   ```
   Narrate as the agent calls its tools: `list_recent_bookings`,
   `list_recent_calls`, `find_double_bookings`, `draft_confirmation_text`,
   `create_staff_task`. Read the final report aloud.
3. Switch to the Veille dashboard → the **"Needs your attention"** panel now
   shows the agent's flagged decisions (the double-booking, the missing service,
   the unresolved urgent call).
4. Click **Done** / **Dismiss** on one — the agent's judgment feeding the product.

### 3:30–4:30 — Why it matters
> "The owner opens the dashboard to a short, prioritized list instead of
> scrolling every overnight call. Routine confirmations are already drafted;
> only the real decisions surface. It's built entirely on AWS — Strands +
> Bedrock + a scheduled GitHub Action — and it's reusable across every business
> Veille serves."

### 4:30–5:00 — Close
> "Autonomous, background, surfaces only decisions — exactly the Agents for
> Humans brief. Live at app.veille.biz, code is MIT-licensed."

## Pitch checklist (required)
- (1) Problem: overnight follow-up busywork.
- (2) Who: small-business owners using an after-hours receptionist.
- (3) Why it matters: hours saved, nothing important missed, only decisions surface.
