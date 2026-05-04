# Claude Code Prompt: Call Type Classification (Situational, Not Behavioral)

I need to classify all 150 sales call transcripts by **call type** -- the situation the rep walked into, defined independently of how the rep handled it. This is a single-field scoring pass that adds one column (`call_type_v2`) to the existing dataset.

## Why this matters

The previous "call_type" field used keyword detection that conflated prospect-side signals with rep behavior, producing unreliable classifications. The structured coding's `opening_style` field is a rep behavior, not a call type. To analyze rep execution within a fixed call situation, we need a call_type field defined purely by the pre-call situation.

## Setup

Input file:
- `[PATH]/behavioral_scored_v2.csv` -- 150 calls already scored on the 23-element behavioral schema. We're adding one new column.

My Anthropic API key: `[YOUR KEY]`

Save output to:
- `behavioral_scored_v3.csv` -- same as v2 plus a new `call_type_v2` column

**Model: `claude-sonnet-4-6`**

**Expected runtime: 10-15 minutes on Tier 1 API rate limits.**

---

## The classification task

For each call, send the transcript to Anthropic API with the prompt below. Add the returned `call_type_v2` value as a new column.

### API call settings
- Endpoint: https://api.anthropic.com/v1/messages
- Model: claude-sonnet-4-6
- Max tokens: 50 (single field, very short response)
- Headers: x-api-key, anthropic-version: 2023-06-01, content-type: application/json

### Classification system prompt (use exact text)

```
You are classifying an Owner.com sales call by the SITUATION the rep walked into, NOT by how the rep handled the call.

Return ONLY one of these five exact values, no quotes, no explanation:

inbound_followup
cold_outreach
confirmation
in_flight_followup
other

DEFINITIONS (apply these strictly, in this priority order):

1. inbound_followup
The prospect took an action that invited contact -- filled out a form, replied to an email, requested information, signed up for something. The rep is responding to that action.
SIGNALS (look for any):
- Prospect-side language referencing their action: "I filled out a form", "I requested", "I reached out"
- Rep referencing the prospect's action: "I saw you put in a request", "you filled out our form", "saw that you reached out", "you scheduled some time", "you replied to my colleague"
- Lead source language indicating inbound interest

2. confirmation
A meeting/demo is already scheduled. The call is logistical -- confirming time, attendees, link, technical setup.
SIGNALS:
- "we have a meeting scheduled for [time]"
- "just confirming our call at [time]"
- "I see you're booked into my calendar for [time]"
- "wanted to make sure you have the link"
The defining feature: a specific scheduled meeting exists and the call is about that meeting's logistics.

3. in_flight_followup
The rep and prospect have had a prior substantive conversation. The rep is continuing or re-engaging that conversation. There is no fresh inbound signal AND no scheduled meeting.
SIGNALS:
- "I tried to give you a call back last week"
- "we spoke a couple weeks ago"
- "you said you were going to speak with [partner/spouse/manager]"
- "circling back on what we discussed"
- Rep has detailed knowledge of the prospect's business circumstances (suggesting prior conversation)
- Sign-up / registration / onboarding logistics for already-closed deals

4. cold_outreach
No prior contact, no inbound signal, no scheduled meeting. The rep is initiating contact for the first time.
SIGNALS:
- Rep introduces self and company as if for the first time
- Rep uses a hook to create interest (referral, research finding, value proposition)
- Prospect responds with confusion or curiosity ("who is this?", "what is this about?")
- No prospect-side language indicating prior interaction
The rep's choice of opening approach (referral, research-led, direct) is irrelevant -- all of those are still cold_outreach if there was no prior contact.

5. other
Use ONLY for calls that don't fit the above:
- Customer service / support calls (existing customer with an issue, not a sales call)
- Wrong number / disconnects / clearly broken calls
- Calls in non-English where you can't classify with confidence

DECISION RULE:
Apply categories 1-4 in order. Use the first one that matches. Use "other" only as a last resort.

If signals conflict (e.g., prospect filled out a form AND there's a scheduled meeting), prioritize the most recent / most specific situation:
- Scheduled meeting exists → confirmation
- No scheduled meeting but inbound signal → inbound_followup
- No scheduled meeting and no inbound but prior conversation → in_flight_followup
- None of the above → cold_outreach

CRITICAL: Do NOT classify based on rep behavior. A rep using a research hook on a cold call is still cold_outreach. A rep on an inbound follow-up doing a poor job is still inbound_followup. The classification is about the situation, not the execution.
```

### User message format
"Classify this call:\n\n{transcript}"

### Processing rules
- Send the FULL transcript for every call -- no truncation
- 1.5 second delay between API calls (Tier 1 pacing)
- For longer transcripts (>10,000 chars), increase delay to 2.5 seconds
- If a 429 rate limit error occurs despite pacing, back off 30 seconds and retry
- Retry each failed call up to 3 times with 2-second backoff
- If still failing after 3 attempts, log error and write empty value for that row
- Print progress every 10 calls
- Validate output: the returned value must be one of the 5 expected strings (case-insensitive). If not, log a warning and use "other".

### Pre-flight check
Before running the full pipeline, send a single test call to verify the API key and model identifier work. If 200, proceed. If 404, stop and report.

---

## Output

Add `call_type_v2` as a new column to behavioral_scored_v3.csv. All other columns from behavioral_scored_v2.csv preserved unchanged.

After the run, print to stdout:
- Total calls classified: X
- Classification errors: X
- Distribution of call_type_v2 values:
  - inbound_followup: X (Y%)
  - cold_outreach: X (Y%)
  - confirmation: X (Y%)
  - in_flight_followup: X (Y%)
  - other: X (Y%)
- Output file saved to: behavioral_scored_v3.csv

---

## Important notes

- Send FULL transcripts -- no truncation
- Output file path same directory as input
- This is a single-field pass. Do NOT re-score the other 23 fields. Just add call_type_v2.
- Use existing rep_id values from input -- don't extract from transcripts
