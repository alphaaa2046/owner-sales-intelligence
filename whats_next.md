# Owner.com Sales Intelligence — What's Next

*Applied AI Lead case study · Alpha Wong · May 2026*

---

The prototype demonstrates the system on a 150-call sample. Several capabilities were deliberately deferred — either because they require production-scale data, integrations not in scope for the case study, or because the right answer depends on findings that would surface during a structured pilot. The items below are what I'd build next, ordered by how I'd sequence them.

---

### 1. Structured pilot to validate behavioral leverage at scale

**What.** Briefed reps vs. matched controls, behavioral scoring on every call, 30-day measurement window. Booking rate as the primary metric.

**How.** Pair 4–6 reps across tenure levels into matched cohorts using rolling baseline rates within their actual call mix. Half use the brief on cold outreach; half don't. Continuous transcript scoring on both groups so we measure not just booking rate but actual behavior change. Sales operations owns the assignment and rotation.

**Why.** The 150-call sample doesn't support a confident point estimate of impact. A pilot is the only way to validate whether the candidate behaviors surfaced by the dashboard actually move bookings when reps act on them. It also produces the first real signal on adoption — does the brief get used, when, by whom — which determines whether the rollout sequencing works.

---

### 2. Live transcript scoring pipeline in Snowflake

**What.** Nightly job that scores every transcript against the 23-field behavioral schema and updates the dashboard backend.

**How.** Snowflake Tasks calling the Anthropic API with the existing scoring prompt; results stored alongside call metadata in the existing `call_transcripts` table. Server-side proxy for API key handling. Dashboard queries the live table on load with caching for performance.

**Why.** The prototype is pre-computed because we don't have live integration. Production needs continuous scoring so confidence labels shift from candidate to confirmed as data accumulates, and so per-rep coaching opportunities surface in something close to real time. This is the unlock that turns the dashboard from a snapshot into a live diagnostic.

---

### 3. Salesloft PCR panel upgrade for the rep companion

**What.** Replace the prototype mockup with a panel inside the existing PCR custom panel that reps already use during dialing.

**How.** Coordinate with the team that owns PCR to add the four-card phase brief as a new tab inside the existing panel. Card content generated server-side from the dashboard's promoted patterns and the restaurant data PCR already surfaces. Rep feedback (👍/👎) persists to a feedback table that informs prompt refinement.

**Why.** Reps don't need another tool. They need better intelligence inside the tool they're already using. Building the brief as a standalone product would create adoption friction we don't need. Integration with PCR also means the brief inherits PCR's existing rep workflow — no training required, no new login, no behavior change.

---

### 4. Manager pattern-promotion workflow

**What.** The View 3 functionality referenced in the dashboard placeholder — where managers review candidate behaviors surfaced from continuous scoring and decide which ones become "best practice" status.

**How.** Sales operations defines the cadence (weekly review? monthly?) and the threshold (does promotion require manager consensus or single-manager judgment?). Promoted patterns flow into the brief automatically. Rep adherence to promoted patterns becomes coachable, with the dashboard surfacing specific calls where adherence gaps appear.

**Why.** This is the operational loop that closes the analytical-to-action gap. The dashboard surfaces signal; managers convert signal to organizational practice; reps execute against promoted practices; adherence data feeds back into manager decisions. Without this workflow, the dashboard is informative but not operational.

---

### 5. CRM funnel connection for downstream metrics

**What.** Pull show rate, close rate, ACV, and time-to-decision from the CRM and join to call-level behavioral data.

**How.** Read access to the relevant CRM tables; mapping logic to align CRM call IDs with transcript call IDs; ETL into the same Snowflake schema that holds behavioral scoring.

**Why.** Booking rate is the leading indicator but not the metric the business cares most about. Show rate, close rate, and revenue per dial are downstream measures that make the system's ROI quantifiable. They also enable the next layer of analysis: which behaviors correlate with closes (not just bookings), which restaurants produce highest-LTV demos, etc.

---

### 6. Scoring schema improvements based on pilot feedback

**What.** V2 of the behavioral scorecard — quality dimensions on every field where binary or categorical scoring loses execution-quality signal, plus prompt refinement based on which scored behaviors actually correlate with downstream outcomes.

**How.** Run the v2 schema in shadow mode alongside the existing one for 30 days. Compare manager judgment on a stratified sample of calls. Refine prompts where disagreement is high. Promote v2 to primary once it outperforms v1 on the manager-validation set.

**Why.** The current scorecard treats some behaviors as binary that have meaningful quality variation (e.g., "specific time proposed" doesn't distinguish "Tuesday at 2pm" from "sometime next week"). Improving scoring quality is the lowest-effort way to surface stronger behavioral signals as the data scales.

---

## Why these were deferred

Each item above was a deliberate scope decision, not an oversight. Items 1, 4, and 5 require organizational coordination outside the case study scope. Items 2 and 3 require production engineering integration. Item 6 depends on running the system at scale long enough to know which scorecard fields need refinement.

The prototype shows the system's intelligence layer (scoring, classification, surfacing) working end-to-end on a snapshot. The next steps move it from snapshot to live, from analytical to operational, and from leading indicators to revenue impact.
