# Owner Sales Intelligence — Case Study Build

*Applied AI Lead case study · Alpha Wong · May 2026*

---

This repo contains the working prototype and supporting documentation for the Applied AI Lead case study. Built for review by Owner's evaluation panel.

The prototype is a two-product system: a manager-facing diagnostic dashboard and a rep-facing companion brief, both powered by behavioral scoring of the 150-call sample provided.

## Repo structure

```
owner-sales-intelligence/
├── README.md                    # this file
├── exec_summary.md              # 1-page executive summary
├── whats_next.md                # what would be built next, and why
├── deliverables/
│   ├── owner_dashboard.html     # Manager Intelligence Dashboard
│   └── owner_brief.html         # Rep Prep Companion (brief)
└── analysis/
    ├── prompts/                 # Claude Code prompts used to build the system
    │   ├── behavioral_scoring.md      # 23-field behavioral scoring prompt
    │   ├── call_type_classifier.md    # situational call type classifier prompt
    │   ├── dashboard_build.md         # canonical dashboard build prompt
    │   └── brief_build.md             # canonical brief build prompt
    ├── scripts/                 # Python scripts that ran the scoring
    │   ├── score_transcripts.py
    │   └── classify_call_types.py
    ├── queries/                 # description of SQL run against Snowflake
    │   └── README.md            # SQL was ad-hoc; this README describes what the queries did
    └── data/
        ├── behavioral_scored.csv  # 150 calls scored on the 23-field schema + call type
        └── README.md              # data provenance
```

## How to view the deliverables

The dashboard and brief are self-contained HTML files. No build step, no server required.

- Open `deliverables/owner_dashboard.html` in any modern browser
- Open `deliverables/owner_brief.html` in any modern browser

Both files run on hardcoded data. No live API calls, no environment configuration needed.

**Suggested order if you have 15 minutes:**

1. Read `exec_summary.md` (~3 minutes)
2. Open the dashboard, click through Views 1, 2, 3 (~7 minutes)
3. Open the brief, switch between 2-3 restaurants in the dropdown (~3 minutes)
4. Skim `whats_next.md` for the production roadmap (~2 minutes)

## How the system works

The pipeline has two stages, both running on transcripts from Owner's Snowflake instance:

**Stage 1 — Behavioral scoring.** Each transcript is scored against a 23-field categorical schema (`research_hook_used`, `prospect_language_mirrored`, `commission_math_specific`, etc.) — the rep behaviors that may correlate with booking. The schema and scoring instructions are in `analysis/prompts/behavioral_scoring.md`. The Python script `analysis/scripts/score_transcripts.py` calls the Anthropic API with this prompt and writes results.

**Stage 2 — Call type classification.** Each transcript is classified into one of four situational categories (cold outreach, inbound follow-up, in-flight follow-up, confirmation) based on signals like prior contact, lead source, and prospect-side language. Classifier prompt in `analysis/prompts/call_type_classifier.md`. Script in `analysis/scripts/classify_call_types.py`.

Both stages output to `analysis/data/behavioral_scored.csv` — the master dataset that powers the dashboard's Views 1 and 2.

The Claude Code prompts in `analysis/prompts/dashboard_build.md` and `analysis/prompts/brief_build.md` are the prompts used to generate the HTML deliverables, with the behavioral and call-type data hardcoded into the files at build time.

## How the prototype differs from production

The prototype demonstrates the system's logic on a 150-call snapshot. Production runs the same logic continuously against live Snowflake data. The intelligence layer (transcript scoring, behavioral classification, dashboard analytics, brief generation) is the same in both. What differs is the integration and operational layers.

| Layer | Prototype | Production |
|---|---|---|
| Dashboard data | Pre-computed; values hardcoded in the HTML, each traceable to its source query | Snowflake nightly job updates the dashboard backend; live refresh on load |
| Brief content | Pre-generated for 10 demo restaurants, hardcoded in the HTML | Generated on-demand from PCR data when the rep opens the call |
| Brief integration | Standalone HTML mockup | Upgrade to existing Salesloft PCR custom panel — not a new tool |
| Behavioral scoring | One-time batch run via API on 150 calls | Snowflake nightly job scoring new transcripts against the same schema |
| Call type classification | LLM classifier on transcripts (situational signals) | CRM `last_interaction` field + lead source data |
| Trend visualizations | Placeholder / illustrative | Time-series from production data with real call timestamps |
| Per-rep flagging | Lifetime windows (across the 150-call sample) | Rolling 30-day windows |
| Rep feedback (👍/👎) on brief | In-browser memory only, not persisted | Persisted to feedback table; informs prompt refinement |
| API key handling | N/A in deliverable HTML files (no live API calls) | Server-side proxy; key never client-side |

The prototype's hardcoded data approach is intentional — it makes the demo reliable and ensures every value shown is traceable to an actual query against the source data. Production removes the snapshot constraint without changing the underlying logic.

## How to re-run the analysis

The Python scripts in `analysis/scripts/` are the canonical versions of what produced the data in `analysis/data/`. Included for transparency, not because re-running them is part of the deliverable.

Requirements:
- Python 3.10+ (no third-party packages — scripts use stdlib only)
- An Anthropic API key (set as `ANTHROPIC_API_KEY` environment variable)
- A CSV export of transcripts from Owner's Snowflake instance (`DEMO_DB.AI_CASE.CALL_TRANSCRIPTS`), with at minimum: `call_id`, `transcript`, `call_outcome`
- A CSV with per-call metadata (cuisine type, restaurant type, num locations, rep tenure, call duration), keyed on `call_id`

The scripts read CSVs from disk; they don't connect to Snowflake directly. Export your Snowflake data first, then run the pipeline:

```bash
export ANTHROPIC_API_KEY=your_key_here

# Stage 1: behavioral scoring (~10 min for 150 calls)
python analysis/scripts/score_transcripts.py \
    --transcripts path/to/transcripts.csv \
    --metadata path/to/metadata.csv \
    --output analysis/data/behavioral_scored.csv

# Stage 2: call type classification (~10 min for 150 calls)
python analysis/scripts/classify_call_types.py \
    --transcripts path/to/transcripts.csv \
    --input analysis/data/behavioral_scored.csv \
    --output analysis/data/behavioral_scored.csv
```

Stage 2 reads the output of Stage 1 and adds a `call_type` column in place. Both scripts include a preflight check that verifies API access before processing begins.

## Data provenance

All data in this repo originates from Owner's Snowflake instance (`DEMO_DB.AI_CASE`). The `analysis/data/behavioral_scored.csv` file contains the 150-call sample with all original Snowflake fields plus:
- 23 behavioral scoring fields produced by Stage 1
- The `call_type` field produced by Stage 2 (situational classification)

The transcripts themselves are not in the repo. They live in Owner's Snowflake. Anyone with access to that instance can reproduce the analysis end-to-end using the scripts and prompts in this repo.

See `analysis/data/README.md` for full provenance notes.

## A note on call type classification

The source Snowflake data does not include a call type field. The `call_type` column in `behavioral_scored.csv` was produced by a situational classifier I built specifically for this analysis.

The classifier went through two iterations:
- An earlier version produced three categories (cold outreach, warm outreach, demo confirmation), which loosely mapped to standard sales taxonomy.
- The current version (in `analysis/prompts/call_type_classifier.md`) produces four categories — cold outreach, inbound follow-up, in-flight follow-up, demo confirmation — based on situational signals like prior contact and prospect-side language. Splitting "warm outreach" into inbound vs. in-flight turned out to matter analytically: the behavioral patterns differ meaningfully between the two.

In the dashboard UI, these display as **Cold outreach**, **Inbound leads**, **Re-engagement**, and **Demo confirmation**. The current classifier is the canonical one; the earlier iteration is documented here for context but is not used downstream.

## Questions

For any questions about the build, contact Alpha Wong.
