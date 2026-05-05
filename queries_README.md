# SQL queries

The analysis used ad-hoc SQL queries against Owner's Snowflake instance (`DEMO_DB.AI_CASE`). The queries themselves were one-off and exploratory, not preserved as canonical scripts.

## What the queries did

The queries fall into two categories:

**Pulling transcripts and metadata for the scoring pipeline.** A single join across `CALL_TRANSCRIPTS` and `RESTAURANTS` to assemble per-call rows with the transcript text, call outcome, restaurant attributes (cuisine type, num_locations, restaurant_type), and rep tenure. This is what fed into `score_transcripts.py` and `classify_call_types.py`.

**Verifying ground-truth metrics during build.** Booking rates by call type, by rep, by cuisine type. Sample-size sanity checks (e.g., "how many calls did rep_08 actually book on cold outreach?"). Manual validation of the LLM-derived call type classifications against the original three-bucket field. These queries surfaced findings that shaped the dashboard's framing — for instance, the 6× spread in booking rate by call type and the rep variance reframing.

## Reproducing

The shape of the queries is straightforward — joins on `call_id` between the two tables, GROUP BY for distributions, COUNT/AVG aggregations for rates. Anyone with access to `DEMO_DB.AI_CASE` can reproduce the data extraction needed for the scoring pipeline with a single SELECT joining the two tables on the relevant key.

The behavioral findings in the dashboard are reproducible from `analysis/data/behavioral_scored.csv` directly without re-running SQL.
