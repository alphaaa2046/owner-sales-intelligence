#!/usr/bin/env python3
"""Score Owner.com sales call transcripts on a 23-field behavioral schema.

Reads transcripts (with associated metadata) from a CSV, calls the Anthropic API
with a structured scoring prompt for each transcript, and writes one row per call
with all 23 behavioral fields populated.

This is the canonical scoring script that produced the behavioral data in
`analysis/data/behavioral_scored.csv`. It is the v2 schema -- expanded from an
earlier 12-field v1 schema after analysis showed binary scoring lost meaningful
execution-quality signal.

Usage:
    export ANTHROPIC_API_KEY=your_key_here
    python score_transcripts.py \\
        --transcripts path/to/transcripts.csv \\
        --metadata path/to/metadata.csv \\
        --output path/to/behavioral_scored.csv

Required columns:
    transcripts CSV: call_id, transcript, call_outcome
    metadata CSV:    call_id, call_type (and optional: rep_tenure, cuisine_type,
                                         restaurant_type, num_locations,
                                         call_duration_min)

The metadata CSV provides per-call context that's referenced in the scoring
prompt (call_type, duration). In practice, the call_type field comes from the
companion classifier (classify_call_types.py).
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

# ------------------------- Config -------------------------

MODEL = "claude-sonnet-4-6"
ENDPOINT = "https://api.anthropic.com/v1/messages"
MAX_TOKENS = 1000

DELAY_SHORT = 1.5
DELAY_LONG = 2.5
LONG_TRANSCRIPT_THRESHOLD = 10_000
RETRY_BACKOFF = 2.0
RATE_LIMIT_BACKOFF = 30.0
MAX_RETRIES = 3

# ------------------------- Schema -------------------------

SCHEMA_FIELDS = [
    "owner_name_used_in_opening",
    "referral_used",
    "referral_specificity",
    "referral_pivot_quality",
    "research_hook_used",
    "discovery_question_asked",
    "discovery_asked_order_source",
    "discovery_asked_marketing",
    "discovery_asked_priority",
    "discovery_asked_other",
    "rep_used_prospect_answer",
    "prospect_language_mirrored",
    "commission_math_specific",
    "third_party_handling",
    "google_visibility_angle_used",
    "social_proof_used",
    "pos_integration_raised",
    "tried_before_objection_handled",
    "no_commitment_close_used",
    "pricing_disclosed_proactively",
    "specific_time_proposed",
    "email_secured",
    "graceful_exit_on_rejection",
]

BOOL_FIELDS = {
    "owner_name_used_in_opening",
    "referral_used",
    "discovery_asked_order_source",
    "discovery_asked_marketing",
    "discovery_asked_priority",
    "discovery_asked_other",
    "no_commitment_close_used",
    "email_secured",
}

# ------------------------- Scoring prompt -------------------------

SCORING_SYSTEM = """You are scoring an Owner.com sales call transcript on 23 rep-controlled behavioral elements organized into 5 phases.

Return ONLY a valid JSON object. No markdown, no explanation, no preamble:

{
  "owner_name_used_in_opening": true | false,
  "referral_used": true | false,
  "referral_specificity": "detailed | basic | not_used",
  "referral_pivot_quality": "strong | weak | not_needed | no_pivot",
  "research_hook_used": "not_used | generic | specific_findings",
  "discovery_question_asked": "before_pitch | after_pitch | none",
  "discovery_asked_order_source": true | false,
  "discovery_asked_marketing": true | false,
  "discovery_asked_priority": true | false,
  "discovery_asked_other": true | false,
  "rep_used_prospect_answer": "explicit | implicit | none",
  "prospect_language_mirrored": "exact_words | paraphrased | not_mirrored",
  "commission_math_specific": "specific_dollars | generic | not_mentioned",
  "third_party_handling": "proactive_reframe | reactive_with_math | reactive_generic | avoided | not_raised",
  "google_visibility_angle_used": "specific | generic | not_used",
  "social_proof_used": "specific_numbers | scale_reference | generic | none",
  "pos_integration_raised": "proactive | reactive | not_applicable | not_raised",
  "tried_before_objection_handled": "handled_well | weak | not_raised",
  "no_commitment_close_used": true | false,
  "pricing_disclosed_proactively": "proactive | reactive | not_applicable",
  "specific_time_proposed": "specific | open_ended | not_reached",
  "email_secured": true | false,
  "graceful_exit_on_rejection": "graceful | abrupt | not_applicable"
}

DEFINITIONS:

PHASE 1 - OPENING SEQUENCE

owner_name_used_in_opening: Did rep use the prospect's first name in the first 30 seconds?
  true: rep addresses prospect by first name early
  false: generic opening, no name use

referral_used: Did rep open with a referral to a nearby restaurant?
  true: "I work with a nearby restaurant called X..."
  false: no referral opening

referral_specificity: How specific was the referral?
  detailed: owner name + restaurant name + location ("I work with John at Tony's down the street")
  basic: just restaurant name ("I work with a place called Tony's")
  not_used: no referral

referral_pivot_quality: When prospect didn't recognize the referral, how did rep handle?
  strong: smooth pivot to research hook or value framing without losing momentum
  weak: stumbled but recovered
  not_needed: prospect recognized the referral
  no_pivot: prospect didn't recognize and rep just kept going without recovery

research_hook_used: Did rep mention pre-call research on THIS specific restaurant?
  specific_findings: rep cites concrete findings (Google ranking position, named competitors, specific review counts, specific website observations)
  generic: rep mentions doing research but no specific findings ("I was looking around at restaurants in the area")
  not_used: no mention of pre-call research

PHASE 2 - DISCOVERY

discovery_question_asked: Did rep ask an open-ended question about the prospect's situation?
  before_pitch: discovery question came BEFORE the product pitch
  after_pitch: discovery question came AFTER the product pitch
  none: no discovery questions, went straight to pitch

discovery_asked_order_source: Did rep ask about where orders are coming from?
  true: "Where are most of your orders coming from?" "Are you doing direct or third-party?"
  false: not asked

discovery_asked_marketing: Did rep ask about marketing or advertising spend?
  true: "Do you spend anything on marketing?" "Are you running ads?"
  false: not asked

discovery_asked_priority: Did rep ask about priorities or top business problem?
  true: "What's your biggest priority right now?" "What's the main challenge?"
  false: not asked

discovery_asked_other: Did rep ask another type of discovery question (POS setup, online presence, customer base)?
  true: any open-ended discovery question not in the categories above
  false: not asked

rep_used_prospect_answer: Did rep adapt the pitch based on what the prospect said in discovery?
  explicit: rep clearly built on the prospect's answer ("you said mostly DoorDash, so let me show you the math on that")
  implicit: rep adapted but didn't explicitly tie back to prospect's answer
  none: rep continued generic pitch regardless of what prospect said

prospect_language_mirrored: Did rep use the prospect's exact words back?
  exact_words: rep repeated prospect's specific phrasing ("OK so getting killed on commissions, exactly what we solve")
  paraphrased: rep referenced what prospect said but in different words
  not_mirrored: rep didn't reference prospect's language

PHASE 3 - VALUE PROPOSITION

commission_math_specific: Did rep calculate actual dollars for THIS restaurant?
  specific_dollars: "if you're doing 250 orders at 25%, that's $1,200-$1,300/month to DoorDash"
  generic: "DoorDash charges high commissions" or "you're paying a lot in fees"
  not_mentioned: commissions never raised by rep

third_party_handling: How did rep handle third-party platform topic (DoorDash, Uber Eats, etc.)?
  proactive_reframe: rep raised third-party platforms BEFORE prospect mentioned them, with reframe
  reactive_with_math: prospect raised it, rep responded with specific commission math
  reactive_generic: prospect raised it, rep responded generically without math
  avoided: prospect raised it, rep deflected or changed topic
  not_raised: third-party platforms never came up

google_visibility_angle_used: Did rep use Google ranking as a hook?
  specific: rep cited ranking position or specific search term
  generic: rep mentioned visibility broadly without specifics
  not_used: not mentioned

social_proof_used: Did rep cite customer results or scale?
  specific_numbers: "X went from $5K to $15K/month"
  scale_reference: "we work with 12,000 restaurants"
  generic: "restaurants see great results"
  none: no social proof referenced

pos_integration_raised: How did rep handle POS systems (Toast, Square, Clover)?
  proactive: rep raised integration before prospect asked
  reactive: addressed after prospect raised it
  not_applicable: no POS mentioned
  not_raised: mentioned but rep ignored

tried_before_objection_handled: Did rep handle the "tried something like this before" objection well?
  handled_well: acknowledged concern, asked for specifics
  weak: deflected or gave generic reassurance
  not_raised: objection didn't come up

PHASE 4 - CLOSE

no_commitment_close_used: Did rep use no-commitment close framing?
  true: "no harm done, just take a look"
  false: not used

pricing_disclosed_proactively: Did rep disclose pricing proactively when relevant?
  proactive: rep gave pricing without prospect asking
  reactive: rep disclosed only when prospect asked
  not_applicable: pricing never came up

specific_time_proposed: Did rep propose a specific day/time for follow-up?
  specific: "Monday at 2pm"
  open_ended: "when works for you"
  not_reached: call ended before close

email_secured: Did rep secure or confirm an email address for follow-up?
  true: email captured or confirmed
  false: no email exchange

PHASE 5 - WRAP

graceful_exit_on_rejection: If prospect declined, how did rep exit?
  graceful: thanked prospect, left door open
  abrupt: ended awkwardly or pushed too hard
  not_applicable: prospect didn't decline / call didn't reach this point
"""

# ------------------------- Helpers -------------------------

REP_RE = re.compile(r"(?:^|\n)(rep_\w+)\s*:")


def extract_rep_id(transcript: str) -> str:
    m = REP_RE.search(transcript)
    return m.group(1) if m else ""


def http_post(payload: dict, api_key: str) -> tuple[int, dict | str]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT,
        data=data,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return e.code, body
    except urllib.error.URLError as e:
        return 0, f"URLError: {e}"


def parse_score_json(text: str) -> dict | None:
    s = text.strip()
    s = re.sub(r"^```(?:json)?", "", s).strip()
    s = re.sub(r"```$", "", s).strip()
    m = re.search(r"\{.*\}", s, flags=re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def normalize_score(d: dict) -> dict:
    out = {}
    for f in SCHEMA_FIELDS:
        v = d.get(f)
        if f in BOOL_FIELDS:
            if isinstance(v, bool):
                out[f] = v
            elif isinstance(v, str):
                out[f] = v.strip().lower() == "true"
            else:
                out[f] = ""
        else:
            out[f] = "" if v is None else str(v).strip()
    return out


def score_call(transcript: str, outcome: str, call_type: str, duration: str, api_key: str) -> dict:
    user_msg = (
        f"Score this complete transcript "
        f"(outcome: {outcome}, call_type: {call_type}, duration: {duration} min):\n\n{transcript}"
    )
    payload = {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "system": SCORING_SYSTEM,
        "messages": [{"role": "user", "content": user_msg}],
    }
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        status, body = http_post(payload, api_key)
        if status == 200 and isinstance(body, dict):
            try:
                text = body["content"][0]["text"]
            except (KeyError, IndexError, TypeError):
                last_err = f"unexpected body: {str(body)[:200]}"
            else:
                parsed = parse_score_json(text)
                if parsed is not None:
                    return normalize_score(parsed)
                last_err = f"json_parse_fail: {text[:200]}"
        elif status == 429:
            print(f"    429 rate limit, sleeping {RATE_LIMIT_BACKOFF}s", flush=True)
            time.sleep(RATE_LIMIT_BACKOFF)
            last_err = "429"
            continue
        else:
            last_err = f"status={status} body={str(body)[:200]}"
        time.sleep(RETRY_BACKOFF)
    print(f"    FAILED after {MAX_RETRIES} attempts: {last_err}", flush=True)
    return {f: "" for f in SCHEMA_FIELDS}


def preflight(api_key: str) -> bool:
    print("Pre-flight: testing API + model id...", flush=True)
    payload = {
        "model": MODEL,
        "max_tokens": 16,
        "messages": [{"role": "user", "content": "ping"}],
    }
    status, body = http_post(payload, api_key)
    if status == 200:
        print("  Pre-flight OK", flush=True)
        return True
    print(f"  Pre-flight FAILED: status={status} body={str(body)[:300]}", flush=True)
    return False


def load_inputs(transcripts_path: str, metadata_path: str) -> list[dict]:
    with open(transcripts_path, newline="") as f:
        transcripts = list(csv.DictReader(f))
    with open(metadata_path, newline="") as f:
        meta = list(csv.DictReader(f))
    type_by_id = {r["call_id"]: r.get("call_type", "") for r in meta}
    meta_by_id = {r["call_id"]: r for r in meta}
    rows = []
    for r in transcripts:
        cid = r["call_id"]
        m = meta_by_id.get(cid, {})
        rows.append({
            "call_id": cid,
            "call_outcome": r["call_outcome"],
            "call_type": type_by_id.get(cid, ""),
            "rep_id": extract_rep_id(r["transcript"]),
            "rep_tenure": m.get("rep_tenure", ""),
            "cuisine_type": m.get("cuisine_type", ""),
            "restaurant_type": m.get("restaurant_type", ""),
            "num_locations": m.get("num_locations", ""),
            "call_duration_min": m.get("call_duration_min", ""),
            "transcript": r["transcript"],
        })
    return rows


def score_all(rows: list[dict], output_path: str, api_key: str) -> int:
    print(f"Scoring {len(rows)} calls on 23-field schema...", flush=True)
    scored_rows: list[dict] = []
    errors = 0
    t0 = time.time()
    for i, r in enumerate(rows, 1):
        scores = score_call(
            r["transcript"], r["call_outcome"], r["call_type"], r["call_duration_min"], api_key
        )
        if all(v == "" for v in scores.values()):
            errors += 1
        merged = {
            "call_id": r["call_id"],
            "call_outcome": r["call_outcome"],
            "call_type": r["call_type"],
            "rep_id": r["rep_id"],
            "rep_tenure": r["rep_tenure"],
            "cuisine_type": r["cuisine_type"],
            "restaurant_type": r["restaurant_type"],
            "num_locations": r["num_locations"],
            "call_duration_min": r["call_duration_min"],
            **scores,
        }
        scored_rows.append(merged)
        delay = DELAY_LONG if len(r["transcript"]) > LONG_TRANSCRIPT_THRESHOLD else DELAY_SHORT
        if i % 10 == 0:
            elapsed = time.time() - t0
            print(f"  {i}/{len(rows)} scored ({errors} errors) — elapsed {elapsed:.0f}s", flush=True)
        time.sleep(delay)

    headers = [
        "call_id",
        "call_outcome",
        "call_type",
        "rep_id",
        "rep_tenure",
        "cuisine_type",
        "restaurant_type",
        "num_locations",
        "call_duration_min",
        *SCHEMA_FIELDS,
    ]
    with open(output_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        for r in scored_rows:
            w.writerow({k: r.get(k, "") for k in headers})
    print(f"Wrote {output_path}", flush=True)
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--transcripts", required=True,
                    help="CSV with call_id, transcript, call_outcome columns")
    ap.add_argument("--metadata", required=True,
                    help="CSV with call_id, call_type, and optional metadata columns")
    ap.add_argument("--output", required=True,
                    help="Output CSV path")
    ap.add_argument("--skip-preflight", action="store_true")
    args = ap.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        print("ERROR: set ANTHROPIC_API_KEY in env", file=sys.stderr)
        return 2

    if not args.skip_preflight:
        if not preflight(api_key):
            return 3

    rows = load_inputs(args.transcripts, args.metadata)
    print(f"Loaded {len(rows)} calls.", flush=True)

    errors = score_all(rows, args.output, api_key)
    print(f"Done. {errors} scoring errors.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
