#!/usr/bin/env python3
"""Classify Owner.com sales calls by situational call type.

Reads transcripts and outputs a call_type label for each call: cold_outreach,
inbound_followup, in_flight_followup, confirmation, or other. The classifier
operates on the SITUATION the rep walked into, not on how the rep handled the
call.

This is the canonical classifier that produced the call_type values in
`analysis/data/behavioral_scored.csv`. It is the v3 iteration -- an earlier
version produced three categories (cold/warm/confirmation), which was found to
lump together meaningfully different conversational situations under "warm."

Usage:
    export ANTHROPIC_API_KEY=your_key_here
    python classify_call_types.py \\
        --transcripts path/to/transcripts.csv \\
        --input path/to/behavioral_scored.csv \\
        --output path/to/behavioral_scored_with_calltype.csv

The input CSV is updated with a new `call_type` column. If the column already
exists, it will be overwritten.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from collections import Counter
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError

MODEL = "claude-sonnet-4-6"
API_URL = "https://api.anthropic.com/v1/messages"
MAX_TOKENS = 50

VALID_LABELS = {
    "inbound_followup", "cold_outreach", "confirmation",
    "in_flight_followup", "other",
}

CLASSIFY_SYSTEM_PROMPT = """You are classifying an Owner.com sales call by the SITUATION the rep walked into, NOT by how the rep handled the call.

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
- Scheduled meeting exists -> confirmation
- No scheduled meeting but inbound signal -> inbound_followup
- No scheduled meeting and no inbound but prior conversation -> in_flight_followup
- None of the above -> cold_outreach

CRITICAL: Do NOT classify based on rep behavior. A rep using a research hook on a cold call is still cold_outreach. A rep on an inbound follow-up doing a poor job is still inbound_followup. The classification is about the situation, not the execution.
"""


def post_messages(payload: dict, api_key: str, timeout: int = 180) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = urlrequest.Request(
        API_URL,
        data=body,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    with urlrequest.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def preflight(api_key: str) -> tuple[bool, str]:
    payload = {
        "model": MODEL,
        "max_tokens": 32,
        "messages": [{"role": "user", "content": "Reply with the single word: ok"}],
    }
    try:
        data = post_messages(payload, api_key, timeout=30)
        text = "".join(b.get("text", "") for b in data.get("content", []))
        return True, text.strip()
    except HTTPError as e:
        return False, f"HTTP {e.code}: {e.read().decode('utf-8', 'ignore')[:300]}"
    except URLError as e:
        return False, f"URL error: {e}"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def normalize_label(text: str) -> str:
    """Strip whitespace/quotes/punctuation and lowercase. Return one of VALID_LABELS or empty string."""
    s = text.strip().strip('"').strip("'").strip(".").strip().lower()
    if "\n" in s:
        s = s.splitlines()[0].strip()
    if " " in s:
        if s not in VALID_LABELS:
            for tok in s.split():
                if tok in VALID_LABELS:
                    return tok
    return s if s in VALID_LABELS else ""


def classify_one(transcript: str, api_key: str, attempts: int = 3) -> tuple[str, str | None]:
    payload = {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "system": CLASSIFY_SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": f"Classify this call:\n\n{transcript}"}],
    }
    last_err = None
    for attempt in range(1, attempts + 1):
        try:
            data = post_messages(payload, api_key, timeout=120)
            text = "".join(b.get("text", "") for b in data.get("content", []))
            label = normalize_label(text)
            if label:
                return label, None
            last_err = f"invalid label: {text[:80]!r}"
        except HTTPError as e:
            body = e.read().decode("utf-8", "ignore")[:200]
            last_err = f"HTTP {e.code}: {body}"
            if e.code == 429:
                time.sleep(30)
                continue
        except (URLError, TimeoutError) as e:
            last_err = f"net: {e}"
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
        if attempt < attempts:
            time.sleep(2)
    return "", last_err


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--transcripts", required=True,
                    help="CSV with call_id and transcript columns")
    ap.add_argument("--input", required=True,
                    help="Existing scored CSV to add call_type column to")
    ap.add_argument("--output", required=True,
                    help="Output CSV path")
    ap.add_argument("--limit", type=int, default=0,
                    help="Cap number of calls (0 = all)")
    ap.add_argument("--skip-preflight", action="store_true")
    args = ap.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        print("ERROR: set ANTHROPIC_API_KEY in env", file=sys.stderr)
        sys.exit(2)

    with open(args.input, newline="", encoding="utf-8") as f:
        input_rows = list(csv.DictReader(f))
        input_cols = list(input_rows[0].keys()) if input_rows else []
    with open(args.transcripts, newline="", encoding="utf-8") as f:
        transcripts = {r["call_id"]: r["transcript"] for r in csv.DictReader(f)}

    missing = [r["call_id"] for r in input_rows if r["call_id"] not in transcripts]
    if missing:
        print(f"ERROR: {len(missing)} rows have no transcript: {missing[:5]}", file=sys.stderr)
        sys.exit(4)

    print(f"loaded: {len(input_rows)} input rows, {len(transcripts)} transcripts", flush=True)

    if not args.skip_preflight:
        ok, msg = preflight(api_key)
        print(f"preflight: ok={ok} | {msg}", flush=True)
        if not ok:
            print("Aborting due to preflight failure.", file=sys.stderr)
            sys.exit(3)

    use_rows = input_rows[:args.limit] if args.limit else input_rows
    n = len(use_rows)
    print(f"classifying {n} calls...", flush=True)

    out_cols = input_cols + (["call_type"] if "call_type" not in input_cols else [])
    out_rows = []
    errors = 0
    label_counts = Counter()
    t0 = time.time()

    for i, row in enumerate(use_rows, start=1):
        cid = row["call_id"]
        transcript = transcripts[cid]
        delay = 2.5 if len(transcript) > 10_000 else 1.5

        label, err = classify_one(transcript, api_key)
        if not label:
            errors += 1
            print(f"  {i}/{n} ERROR call_id={cid}: {err}", flush=True)
            label_value = ""
        else:
            label_value = label
            label_counts[label] += 1

        new_row = dict(row)
        new_row["call_type"] = label_value
        out_rows.append(new_row)

        if i % 10 == 0 or i == n:
            print(f"  {i}/{n} done (errors so far: {errors})", flush=True)
        if i < n:
            time.sleep(delay)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=out_cols)
        w.writeheader()
        for r in out_rows:
            w.writerow({k: r.get(k, "") for k in out_cols})

    elapsed = time.time() - t0
    print("---")
    print(f"Total calls classified: {n}")
    print(f"Classification errors: {errors}")
    print("Distribution:")
    for lab in ["cold_outreach", "inbound_followup", "in_flight_followup", "confirmation", "other"]:
        c = label_counts.get(lab, 0)
        pct = (c / n * 100) if n else 0
        print(f"  {lab}: {c} ({pct:.1f}%)")
    print(f"Output: {args.output}")
    print(f"Elapsed: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
