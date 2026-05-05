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

### 6. Per-call-type schema derivation (inbound leads first, then re-engagement and demo confirmation)

**What.** Derive a complete behavioral schema for each call type the system handles, starting with inbound leads (where the dashboard currently shows a 10-field preview), then re-engagement and demo confirmation. Each schema captures rep behaviors specific to that call type's conversational dynamic.

**How.** For each call type, read 25-30 transcripts in detail across booked and not-booked outcomes. Catalog where rep behavior could vary; note where outcomes diverged. Translate the findings into a structured scoring prompt parallel to the cold outreach prompt in `analysis/prompts/behavioral_scoring.md`. Run the new prompt against the call type's transcripts to score them. Surface the resulting differentials in the dashboard's View 2 alongside cold outreach.

The inbound leads preview already documents 10 candidate behaviors (e.g., `inbound_action_referenced_specifically`, `specialist_handoff_framing`, `partner_inclusion_handled`) — these would be validated and refined in this pass before scoring.

In parallel: refine the cold outreach schema where binary scoring loses execution-quality signal (e.g., "specific time proposed" doesn't distinguish "Tuesday at 2pm" from "sometime next week"). Run refined prompts in shadow mode against the existing schema; compare to manager judgment on a stratified sample; promote when refined version outperforms.

**Why.** Cold outreach is the highest-volume, lowest-yielding call type — the right place to start. But applying cold outreach coaching to inbound leads is a category mistake. Cold outreach is a hunter motion (create interest, overcome skepticism, close to demo). Inbound is a qualifier motion (the prospect already raised their hand; the rep's job is to qualify fit and schedule fast). The behaviors that matter are different. Until each call type has its own derived schema, the dashboard's coaching guidance for non-cold call types is at best partial and at worst misleading.

---

### 7. Restaurant-attribute-to-phase mapping (intelligent default selection in the brief)

**What.** Replace the prototype's hardcoded default-expanded-phase logic with a learned mapping from restaurant attributes (cuisine, location count, third-party platforms, fit tier, lead source, prior interactions, etc.) to which call phase has the highest leverage for a given restaurant.

**How.** Same analytical engine as behavioral scoring, with the input and target swapped. Per-call categorical evaluation of restaurant attributes against ground-truth booking outcomes; aggregate to surface which phase carries the most leverage for each restaurant attribute combination. Start with a rule-based V1 encoding the heuristics already in the prototype (e.g., "cold outreach + 2+ third-party platforms → expand Pitch with third-party handler"); promote to a learned predictor as outcomes accumulate. Managers retain an override layer to align defaults with what they're emphasizing in coaching that quarter.

This builds on top of Owner's existing concept-fit and pickup-prediction work rather than duplicating it: those models predict WHO will book; this layer predicts WHERE the rep should focus during the call. Different question, different target, complementary intelligence.

**Why.** The prototype's defaults are my judgment about which phase has the highest leverage for each restaurant. They're informed but not validated against booking outcomes. A learned mapping makes the brief's intelligence adaptive — every booking outcome refines what gets shown to the next rep on a similar restaurant. Without this layer, the brief is static; with it, the brief gets sharper over time the same way the dashboard does.

---

## Why these were deferred

Each item above was a deliberate scope decision, not an oversight. Items 1, 4, and 5 require organizational coordination outside the case study scope. Items 2 and 3 require engineering integration. Items 6 and 7 require either qualitative analytical work (per-call-type schema derivation) or accumulated outcome data (restaurant-attribute mapping) that can only happen as the system runs at scale.

The prototype shows the system's intelligence layer (scoring, classification, surfacing) working end-to-end on a snapshot. The next steps move it from snapshot to validated, from analytical to operational, and from leading indicators to revenue impact.
