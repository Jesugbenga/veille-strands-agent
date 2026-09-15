# Architecture

Veille is an after-hours AI receptionist. The **real-time voice** work is handled
by Vapi; the **Veille app** (Next.js) persists everything to Supabase; and the
**autonomous Strands agent** (this repo) runs in the background on that same data,
clearing routine follow-up and surfacing only the decisions a human must make.

```mermaid
flowchart TB
  subgraph Users
    C["Customer<br/>(phone / SMS)"]
    O["Business owner"]
  end

  subgraph Voice["Real-time voice — Vapi"]
    V["Vapi assistant<br/>speech + LLM"]
  end

  subgraph AppLayer["Veille app — Next.js on Vercel"]
    WH["/api/vapi/webhook<br/>call started / ended"]
    TL["/api/vapi/tools<br/>check_availability<br/>book_appointment<br/>request_reschedule"]
    SMS["/api/twilio/sms"]
    DASH["Dashboard<br/>calls · calendar ·<br/>Needs your attention"]
  end

  subgraph DataLayer["Supabase — Postgres + RLS"]
    DB[("businesses · calls · bookings<br/>veille_appointments · integrations<br/>agent_tasks")]
  end

  subgraph Ext["External services"]
    GC["Google Calendar<br/>(one-way mirror)"]
    TW["Twilio SMS"]
    SUM["Groq / Gemini / Mistral<br/>call summaries"]
  end

  subgraph Agent["Autonomous agent — AWS Strands SDK (Python)"]
    SCH["Schedule<br/>GitHub Action / EventBridge"]
    AG["Agent loop"]
    BR["Amazon Bedrock<br/>Nova Lite"]
    TOOLS["Tools:<br/>list bookings/calls ·<br/>find double-bookings ·<br/>draft confirmations ·<br/>create staff tasks"]
  end

  C -->|call / text| V
  C -->|SMS| SMS
  V --> WH
  V --> TL
  WH --> DB
  WH --> SUM
  TL --> DB
  TL --> GC
  TL --> TW
  SMS --> DB

  O --> DASH
  DASH <-->|RLS-scoped| DB

  SCH --> AG
  AG --> BR
  AG --> TOOLS
  TOOLS <-->|"Supabase REST<br/>(service role)"| DB
  DB -->|agent_tasks| DASH
```

## Request flows

**Live call (Vapi):** Customer calls → Vapi runs the conversation → on
availability/booking it calls `/api/vapi/tools` (writes `bookings` +
`veille_appointments`, mirrors to Google Calendar) → on hang-up
`/api/vapi/webhook` writes the `calls` row + an LLM summary. The owner sees it
live on the dashboard (Supabase Realtime, RLS-scoped).

**Autonomous agent (this repo):** On a schedule, the Strands agent loop (on
Amazon Bedrock / Nova) reads the last 24h of `calls` + `bookings` via its tools,
drafts confirmations for the clear ones, detects conflicts/ambiguities, and
writes only the human-decisions into `agent_tasks`. Those appear in the
dashboard's **"Needs your attention"** panel.

## Key properties
- **Separation of concerns:** Vapi owns real-time voice; the Strands agent owns
  autonomous back-office work. Neither blocks the other.
- **Single source of truth:** Supabase. The agent talks to it over REST with the
  service-role key; the dashboard reads it under row-level security.
- **AWS-native agent:** Strands Agents SDK + Amazon Bedrock (Nova), scheduled via
  a GitHub Action (or AWS Lambda + EventBridge).
