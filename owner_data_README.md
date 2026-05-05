# Data — Provenance and Schema

## File: `behavioral_scored.csv`

The master dataset that powers the dashboard. 150 rows, one per call.

### Origin

Source transcripts come from Owner's Snowflake instance: `DEMO_DB.AI_CASE.CALL_TRANSCRIPTS`. The transcripts themselves are not in this repo; the SQL used to pull them is at `analysis/queries/owner_calls.sql`.

This CSV is produced by running:
1. `analysis/scripts/classify_call_types.py` (uses prompt `analysis/prompts/call_type_classifier.md`) — adds `call_type` field to each call
2. `analysis/scripts/score_transcripts.py` (uses prompt `analysis/prompts/behavioral_scoring.md`) — scores transcripts on the cold-outreach behavioral schema

Both scripts call the Anthropic API and write their outputs to this CSV.

The 150-call sample includes all four call types. The 23-field behavioral schema embedded in `behavioral_scoring.md` is **cold-outreach-derived** — see the methodology notes in the main README. Production would maintain separate schemas per call type. The behavioral fields in this CSV reflect the cold-outreach schema applied across the full 150-call sample for prototype demonstration.

### Schema

#### Original Snowflake fields (provided by Owner)

| Column | Type | Description |
|---|---|---|
| `call_id` | string | Unique call identifier |
| `call_outcome` | string | `demo_booked` or `not_booked` (CRM ground truth) |
| `rep_id` | string | Anonymized rep identifier (rep_01 through rep_15) |
| `rep_tenure` | string | `senior`, `mid`, or `new` |
| `cuisine_type` | string | Restaurant cuisine (American, Mexican, Italian, etc.) |
| `restaurant_type` | string | `full_service`, `quick_service`, etc. |
| `num_locations` | integer | Number of locations the restaurant operates |
| `call_duration_min` | float | Call length in minutes |

#### Behavioral scoring fields (produced by `score_transcripts.py`)

23 categorical fields scored from the transcript. Each captures a specific rep behavior. Full definitions are in `analysis/prompts/behavioral_scoring.md`.

| Phase | Fields |
|---|---|
| Opening | `owner_name_used_in_opening`, `referral_used`, `referral_specificity`, `referral_pivot_quality`, `research_hook_used` |
| Discovery | `discovery_question_asked`, `discovery_asked_order_source`, `discovery_asked_marketing`, `discovery_asked_priority`, `discovery_asked_other`, `rep_used_prospect_answer`, `prospect_language_mirrored` |
| Pitch | `commission_math_specific`, `third_party_handling`, `google_visibility_angle_used`, `social_proof_used`, `pos_integration_raised`, `tried_before_objection_handled` |
| Close | `no_commitment_close_used`, `pricing_disclosed_proactively`, `specific_time_proposed`, `email_secured`, `graceful_exit_on_rejection` |

#### Call type field (produced by `classify_call_types.py`)

| Column | Values |
|---|---|
| `call_type` | `cold_outreach`, `inbound_followup`, `in_flight_followup`, `confirmation`, `other` |

### Distribution

| call_type | Count | % | Booking rate |
|---|---|---|---|
| cold_outreach | 79 | 53% | 12.7% |
| inbound_followup | 39 | 26% | 48.7% |
| in_flight_followup | 20 | 13% | 65.0% |
| confirmation | 9 | 6% | 77.8% |
| other | 3 | 2% | 66.7% |
| **Total** | **150** | **100%** | **34.0%** |

### Reproducing the data

To regenerate the CSV from scratch (assuming an Anthropic API key and CSV exports of the source transcripts):

```bash
export ANTHROPIC_API_KEY=your_key_here
python ../scripts/classify_call_types.py    # Stage 1: classify call types
python ../scripts/score_transcripts.py      # Stage 2: score on cold-outreach schema
```

Each script takes ~10 minutes for 150 calls. Run classification first; the call_type field is read by downstream tooling. The current scoring step uses the cold-outreach schema regardless of the call's actual type — the prototype scores the full sample for demonstration. Production would filter to cold-outreach calls before scoring, and run separate scoring jobs for other call types using their own derived schemas.
