# Dashboard Build Prompts — Combined

This file consolidates the 7 Claude Code prompts used to build and iterate on `owner_dashboard.html`. They are presented in chronological order; each section header notes what that iteration did and why. The final dashboard reflects all of these prompts applied in sequence to a single HTML file.

For someone re-implementing the dashboard from scratch, the cleanest approach is to read all sections sequentially, then implement against the cumulative spec. Earlier iterations established the foundation (layout, data structures, styling); later iterations refined specific elements (chart consolidation, behavior table de-duplication, view rename, tooltips, sticky header).

---

## Iteration 1 — Phase 1 build (foundation)

The original Phase 1 dashboard build prompt. Establishes the three-view structure (Call outcomes / Behavior insights / Coaching opportunities), data structures, AI insight panels, headline stats, the rep × call type heatmap, and the View 2 behavior comparison table. View 3 is a placeholder.

# Claude Code Prompt: Owner Sales Intelligence Dashboard (Phase 1)

Build a single-file HTML dashboard demonstrating the Owner sales intelligence prototype. Phase 1 covers Views 1 and 2 (Performance & Flagging, What's Working / What's Not). Phase 2 (Candidate Patterns) is a separate prompt; build hooks for it but don't implement its content.

## Output

Single file: `owner_dashboard.html` -- self-contained HTML with embedded CSS and JS. No build step. Opens directly in a browser. Uses Chart.js (CDN) for charts.

Save to the current working directory.

## Data approach

**All data is pre-computed and hardcoded in the HTML as JS objects.** Do NOT read from CSVs at runtime. Do NOT make API calls. Every number in this prompt comes from real analysis on the 150-call corpus and should be embedded literally.

This matches the prototype-vs-production framing in the case study: prototype is hardcoded for demo reliability; production runs the same logic against live Snowflake queries refreshing nightly.

## Visual style

- Manager-facing, not engineer-facing. Clean, scannable, no jargon.
- Colors: dark text on white background; one accent color (Owner uses a teal/green -- pick something close to `#0E7C66` or similar). Use red sparingly for "below baseline" indicators.
- Sans-serif font stack: `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif`
- Comfortable spacing -- this is going on a manager's screen, not a phone
- Tab-style nav at the top to switch between Views 1, 2, and (placeholder) 3
- Each view has its own URL hash so refreshing a view doesn't reset to View 1
- Confidence labels render as small pills next to each metric: ✓ Confirmed, → Directional, ? Candidate, ⊘ Insufficient

## Top of page (persistent across views)

A header strip with:
- Title: "Owner Sales Intelligence -- Manager Dashboard"
- Subtitle: "Prototype on 150-call sample. Production scales with continuous transcript scoring."
- Tab nav: View 1 (Performance & Flagging) / View 2 (What's Working) / View 3 (Candidate Patterns) [placeholder, shows "Coming in Phase 2" panel]

## VIEW 1: Performance & Flagging

This is the headline view. Pipeline stage is the primary axis -- raw "booking rate by rep" without controlling for call mix is misleading and is NOT the headline chart.

### Section 1.1 -- Headline numbers strip

Four large stat cards across the top:

| Card | Value | Label | Trend (placeholder) |
|---|---|---|---|
| 1 | 150 | Calls in sample | -- (no historical) |
| 2 | 51 (34.0%) | Demos booked | ↗ placeholder up arrow |
| 3 | 5x | Spread between cold and confirmation booking rates | -- |
| 4 | 79 | Cold outreach calls (largest bucket; lowest rate) | -- |

Below the cards: a small italic line: *Trend indicators are placeholders -- no timestamps in this 150-call snapshot. Production pulls trends from call timestamps; data refreshes nightly.*

### Section 1.2 -- AI-generated insight panel

A bordered callout box with light-tinted background (use the accent color at ~5% opacity).

Content (hardcoded, exact text):

> **What this view is showing**
>
> Booking rate at this sample is 34.0%, but that aggregate hides the real signal: pipeline stage drives a 6x spread. Cold outreach books at 12.7%; confirmation books at 77.8%. The "top performers" by raw booking rate are mostly assigned to higher-baseline call types -- rep_01's 100% rate reflects an in-flight follow-up queue (65% baseline), not behavioral signature.
>
> **Where to look:** the rep × call type heatmap below, filtering on cold outreach or inbound follow-up where execution variance has the most room to move.
>
> *In production, this insight regenerates as data updates. Current text is pre-generated for demo.*

### Section 1.3 -- Booking rate by call type (the headline chart)

A horizontal bar chart. Title: "Where bookings come from -- and where they don't."

Data:
```js
const callTypeData = [
  {label: "Confirmation", n: 9, booked: 7, rate: 77.8, confidence: "candidate"},
  {label: "In-flight follow-up", n: 20, booked: 13, rate: 65.0, confidence: "directional"},
  {label: "Inbound follow-up", n: 39, booked: 19, rate: 48.7, confidence: "directional"},
  {label: "Cold outreach", n: 79, booked: 10, rate: 12.7, confidence: "directional"},
  {label: "Other", n: 3, booked: 2, rate: 66.7, confidence: "insufficient"}
];
```

Bar labels show: `{rate}% (n={n}, {booked} booked)` plus the confidence pill.

Below the chart, small italic text: *Confidence reflects current sample size. Cold outreach is "directional" because n=79 is enough to read the 12.7% rate as real but not enough to confirm the spread is causal at field-level. At production volume (~1,440 dials/day), all five rows tighten within weeks.*

### Section 1.4 -- Rep × call type heatmap

A heatmap or cross-tabulated table. Each cell shows: booking rate, with cell n in small text. Rows are reps, columns are the 4 main call types (confirmation, in-flight followup, inbound followup, cold outreach -- skip "other"). Cells with n=0 are empty/gray. Cells with 1<=n<5 are pale-tinted; cells with n>=5 are full-color.

Cell color logic:
- If n=0: gray/empty
- If n>=1 and rate < (call type baseline - 10pts): light red tint
- If n>=1 and rate within ±10pts of baseline: neutral
- If n>=1 and rate > (call type baseline + 10pts): light green tint
- Cell text shows the rate (no decimal -- "100%" not "100.0%") with smaller "n=X" below

Data (this is the rep × call_type cross-tab from the dataset):

```js
const heatmapData = {
  "rep_01": { "in_flight_followup": {n:7, booked:7, rate:100} },
  "rep_02": { "cold_outreach": {n:8, booked:1, rate:12.5}, "inbound_followup": {n:3, booked:3, rate:100} },
  "rep_03": { "cold_outreach": {n:16, booked:2, rate:12.5}, "in_flight_followup": {n:2, booked:1, rate:50}, "inbound_followup": {n:1, booked:1, rate:100} },
  "rep_04": { "cold_outreach": {n:7, booked:1, rate:14.3}, "in_flight_followup": {n:1, booked:0, rate:0}, "inbound_followup": {n:1, booked:0, rate:0} },
  "rep_05": { "in_flight_followup": {n:2, booked:2, rate:100}, "inbound_followup": {n:1, booked:0, rate:0} },
  "rep_06": { "cold_outreach": {n:9, booked:1, rate:11.1}, "in_flight_followup": {n:2, booked:0, rate:0}, "inbound_followup": {n:4, booked:2, rate:50} },
  "rep_07": { "cold_outreach": {n:9, booked:0, rate:0}, "in_flight_followup": {n:1, booked:0, rate:0}, "inbound_followup": {n:1, booked:1, rate:100} },
  "rep_08": { "cold_outreach": {n:21, booked:4, rate:19.0}, "in_flight_followup": {n:2, booked:1, rate:50}, "inbound_followup": {n:1, booked:1, rate:100} },
  "rep_09": { "confirmation": {n:4, booked:3, rate:75}, "inbound_followup": {n:5, booked:4, rate:80} },
  "rep_10": { "inbound_followup": {n:2, booked:2, rate:100} },
  "rep_11": { "confirmation": {n:2, booked:1, rate:50}, "in_flight_followup": {n:1, booked:1, rate:100}, "inbound_followup": {n:7, booked:2, rate:28.6} },
  "rep_12": { "cold_outreach": {n:1, booked:1, rate:100}, "confirmation": {n:2, booked:2, rate:100}, "inbound_followup": {n:4, booked:2, rate:50} },
  "rep_13": { "inbound_followup": {n:7, booked:1, rate:14.3} },
  "rep_14": { "cold_outreach": {n:7, booked:0, rate:0}, "in_flight_followup": {n:1, booked:0, rate:0} },
  "rep_15": { "inbound_followup": {n:2, booked:0, rate:0} }
};

const callTypeBaselines = {
  cold_outreach: 12.7,
  inbound_followup: 48.7,
  in_flight_followup: 65.0,
  confirmation: 77.8
};
```

Title above heatmap: "Each rep's booking rate within each call type"
Subtitle: "Compares against call-type baseline to show execution gap independent of call mix"

### Section 1.5 -- Reps to flag

A table or card list of reps who are notably below baseline within their actual call mix. "Notably below" = booking rate at least 10 pts under baseline AND n>=5 in that call type.

Each flagged rep gets a card with:
- Rep ID + tenure (look up from data)
- Why flagged: "Booking rate {X}% on {N} cold outreach calls -- baseline is 12.7%"
- Note: "Investigate via View 3 once Phase 2 is deployed -- behavioral patterns within cold outreach"

Reps to flag based on the data:

```js
const flaggedReps = [
  {rep: "rep_07", tenure: "mid", reason: "0% booking on 9 cold outreach calls (baseline 12.7%)", calltype: "cold_outreach"},
  {rep: "rep_14", tenure: "new", reason: "0% booking on 7 cold outreach calls (baseline 12.7%)", calltype: "cold_outreach"},
  {rep: "rep_13", tenure: "new", reason: "14.3% booking on 7 inbound follow-up calls (baseline 48.7%)", calltype: "inbound_followup"},
  {rep: "rep_15", tenure: "new", reason: "0% booking on 2 inbound follow-up calls (small sample, monitor)", calltype: "inbound_followup", warn: "small sample"}
];
```

Note above the list: "Flags are computed within call type. Lifetime windows in the prototype; production uses rolling 30-day windows."

### Section 1.6 -- Filters (top of view 1)

Filter controls (these don't actually re-filter the data in Phase 1 -- they're UI placeholders that show how filtering works in production):

- Call type: All / Cold outreach / Inbound follow-up / In-flight follow-up / Confirmation
- Cuisine: All / American / Mexican / Italian / unknown / other
- Tenure: All / Senior / Mid / New
- Timeframe: All time (default) / Last 7 days / Last 30 days / Last 90 days

When changed: show a small toast "Filter applied (would re-render in production)" and don't actually re-render the charts. Add a small (i) tooltip explaining: "In the prototype, all data shown is the full 150-call snapshot. Production filters re-aggregate from Snowflake nightly tables."

## VIEW 2: What's Working / What's Not

### Section 2.1 -- Filter at top (this one DOES filter)

A pill-style segmented control:

[ Cold outreach (default) ] [ Inbound follow-up ] [ In-flight follow-up (limited data) ] [ Confirmation (limited data) ]

When selected, the entire view re-renders with that call type's data. **Cold outreach is the default selection** since aggregating across call types produces misleading correlations.

### Section 2.2 -- AI-generated insight panel

Same styling as View 1's insight panel. Contents change by selected call type:

```js
const insightByCallType = {
  cold_outreach: "Within cold outreach (n=79, 10 booked), behaviors that show the strongest signal at this sample are: paraphrasing the prospect's words back (mirroring), proposing a specific time for follow-up, citing specific findings about the restaurant, explicitly building on the prospect's discovery answer (adaptation), and using a proactive third-party reframe. Note that adaptation and mirroring are related but distinct -- adaptation can occur without mirroring, and the combination is a stronger signal than either alone (50% of booked cold calls do both vs 19% of not-booked). All findings are 'candidate' at current N -- the 10 booked calls aren't enough to confirm causal weight. At production volume, these resolve within weeks.",
  inbound_followup: "Within inbound follow-up (n=39, 19 booked), the strongest signals are: discovery questions asked BEFORE pitching (+27pts), proposing specific times rather than open-ended (+27pts), and explicitly building on the prospect's discovery answer (+16pts). Sample is more balanced here (19 vs 20) so signal is cleaner. The pattern: warm prospects book more often when reps slow down to qualify before pitching.",
  in_flight_followup: "n=20 (13 booked, 7 not-booked). Sample is too small for confident behavioral comparison within this call type. The dashboard surfaces what's available with explicit insufficient-data labels.",
  confirmation: "n=9 (7 booked, 2 not-booked). Sample insufficient for behavioral comparison. Production data will populate this view within weeks."
};
```

### Section 2.3 -- Behavioral comparison table

A sortable table. Columns: Behavior / Value / Booked rate / Not-booked rate / Differential / N booked / N not-booked / Confidence.

**Default sort: differential descending.**

Data for cold_outreach (n=10 booked, n=69 not-booked):

```js
const behaviorTable_cold = [
  {field: "prospect_language_mirrored", value: "paraphrased", booked_rate: 50.0, nb_rate: 17.4, diff: 32.6, n_b: 10, n_nb: 69, confidence: "candidate"},
  {field: "specific_time_proposed", value: "specific", booked_rate: 50.0, nb_rate: 17.4, diff: 32.6, n_b: 10, n_nb: 69, confidence: "candidate"},
  {field: "research_hook_used", value: "specific_findings", booked_rate: 60.0, nb_rate: 31.9, diff: 28.1, n_b: 10, n_nb: 69, confidence: "candidate"},
  {field: "rep_used_prospect_answer", value: "explicit", booked_rate: 30.0, nb_rate: 2.9, diff: 27.1, n_b: 10, n_nb: 69, confidence: "candidate"},
  {field: "google_visibility_angle_used", value: "specific", booked_rate: 40.0, nb_rate: 15.9, diff: 24.1, n_b: 10, n_nb: 69, confidence: "candidate"},
  {field: "third_party_handling", value: "proactive_reframe", booked_rate: 70.0, nb_rate: 46.4, diff: 23.6, n_b: 10, n_nb: 69, confidence: "candidate"},
  {field: "referral_specificity", value: "detailed", booked_rate: 50.0, nb_rate: 30.4, diff: 19.6, n_b: 10, n_nb: 69, confidence: "candidate"},
  {field: "commission_math_specific", value: "specific_dollars", booked_rate: 20.0, nb_rate: 1.4, diff: 18.6, n_b: 10, n_nb: 69, confidence: "candidate"},
  {field: "discovery_question_asked", value: "before_pitch", booked_rate: 40.0, nb_rate: 26.1, diff: 13.9, n_b: 10, n_nb: 69, confidence: "candidate"},
  {field: "pos_integration_raised", value: "reactive", booked_rate: 40.0, nb_rate: 26.1, diff: 13.9, n_b: 10, n_nb: 69, confidence: "candidate"},
  {field: "social_proof_used", value: "generic", booked_rate: 30.0, nb_rate: 18.8, diff: 11.2, n_b: 10, n_nb: 69, confidence: "candidate"}
];
```

Data for inbound_followup (n=19 booked, n=20 not-booked):

```js
const behaviorTable_inbound = [
  {field: "specific_time_proposed", value: "specific", booked_rate: 42.1, nb_rate: 15.0, diff: 27.1, n_b: 19, n_nb: 20, confidence: "directional"},
  {field: "discovery_question_asked", value: "before_pitch", booked_rate: 42.1, nb_rate: 15.0, diff: 27.1, n_b: 19, n_nb: 20, confidence: "directional"},
  {field: "rep_used_prospect_answer", value: "explicit", booked_rate: 21.1, nb_rate: 5.0, diff: 16.1, n_b: 19, n_nb: 20, confidence: "directional"},
  {field: "prospect_language_mirrored", value: "paraphrased", booked_rate: 47.4, nb_rate: 35.0, diff: 12.4, n_b: 19, n_nb: 20, confidence: "directional"},
  {field: "rep_used_prospect_answer", value: "none", booked_rate: 42.1, nb_rate: 65.0, diff: -22.9, n_b: 19, n_nb: 20, confidence: "directional"},
  {field: "specific_time_proposed", value: "not_reached", booked_rate: 15.8, nb_rate: 35.0, diff: -19.2, n_b: 19, n_nb: 20, confidence: "directional"},
  {field: "discovery_question_asked", value: "none", booked_rate: 26.3, nb_rate: 45.0, diff: -18.7, n_b: 19, n_nb: 20, confidence: "directional"},
  {field: "prospect_language_mirrored", value: "not_mirrored", booked_rate: 47.4, nb_rate: 65.0, diff: -17.6, n_b: 19, n_nb: 20, confidence: "directional"}
];
```

For in_flight_followup and confirmation: render the table with a single row that says "Sample insufficient (n_booked=X, n_notbooked=Y). View becomes meaningful at production scale."

Visual touches:
- Color the differential column: green for positive, red for negative, gray for ±5pts
- Hover tooltip on the field name shows the field's definition (use abbreviated definitions from the scoring schema)

### Field tooltip content (used on hover in the behavior table)

```js
const fieldTooltips = {
  rep_used_prospect_answer: "Did the rep adapt the pitch based on the prospect's discovery answer? This measures CONTENT adaptation -- did the rep change what they said next based on what the prospect told them. Distinct from prospect_language_mirrored, which measures whether the rep echoed the prospect's exact words.",
  prospect_language_mirrored: "Did the rep echo the prospect's exact words back? This measures LANGUAGE mimicry. A rep can adapt content (rep_used_prospect_answer) without mirroring language, but mirroring language usually implies content adaptation. Both behaviors co-occur in 50% of booked cold calls vs 19% of not-booked.",
  research_hook_used: "Did the rep open with a specific finding about THIS restaurant? specific_findings = cited concrete details (Google ranking, named competitors). generic = mentioned doing research without findings. not_used = no research mention.",
  specific_time_proposed: "Did the rep propose a specific day/time for follow-up? specific = 'Monday at 2pm.' open_ended = 'when works for you.' not_reached = call ended before close.",
  third_party_handling: "How the rep handled DoorDash/Uber Eats topic. proactive_reframe = rep raised it first with a reframe. reactive_with_math = prospect raised it, rep used dollar math. reactive_generic = rep acknowledged without math. avoided = rep deflected. not_raised = third-party never came up.",
  google_visibility_angle_used: "Did the rep use Google ranking as a hook? specific = cited ranking position or search term. generic = mentioned visibility broadly. not_used = not mentioned.",
  commission_math_specific: "Did the rep do specific commission math for THIS restaurant? specific_dollars = '$1,200/month at 25% on 250 orders.' generic = 'commissions are high.' not_mentioned = commissions never raised by rep.",
  discovery_question_asked: "Did the rep ask an open-ended discovery question? before_pitch = asked before pitching. after_pitch = asked after the pitch was already underway. none = no discovery questions.",
  pos_integration_raised: "How the rep handled Toast/Square/Clover. proactive = rep raised integration before prospect asked. reactive = addressed after prospect raised it. not_applicable = no POS mentioned. not_raised = mentioned but rep ignored.",
  referral_specificity: "How specific the referral opener was. detailed = owner name + restaurant + location. basic = just restaurant name. not_used = no referral opener.",
  social_proof_used: "Cited customer results or scale. specific_numbers = 'X went from $5K to $15K/mo.' scale_reference = 'we work with 12,000 restaurants.' generic = 'restaurants see great results.' none = no social proof.",
  referral_used: "Did the rep open with a nearby restaurant referral? Binary True/False."
};
```

Apply the tooltip on the FIELD name only (not the value). On hover, show the matching content from this map. If a field isn't in the map, show "Field definition not available -- check the schema appendix."

### Section 2.4 -- Phrase frequency comparison

A small table or list. For cold outreach, top 8 phrases by differential. Columns: Phrase / In booked calls / In not-booked / Unique reps.

```js
const phrasesByCallType = {
  cold_outreach: [
    {phrase: "give you a call", b: 9, nb: 1, reps: 7, note: "callback / next step language"},
    {phrase: "wanted to reach out", b: 4, nb: 0, reps: 3, note: "conversational opener"},
    {phrase: "send you an email", b: 6, nb: 0, reps: 5, note: "follow-up handoff"},
    {phrase: "if it makes sense", b: 4, nb: 0, reps: 2, note: "soft check-in language"},
    {phrase: "learn a little bit more", b: 4, nb: 0, reps: 2, note: "discovery framing"}
  ],
  inbound_followup: [
    {phrase: "saw that you", b: 8, nb: 3, reps: 4, note: "acknowledging the inbound signal"}
  ]
};
```

For sparse call types (in_flight, confirmation): "Phrase analysis insufficient at current sample."

Caveat below: *Phrases are inductively extracted (n-grams of length 4-8 across rep utterances). They surface what was actually said in booked calls, not what's prescribed. Production: same approach run nightly across the full call corpus.*

## VIEW 3 (placeholder)

Just a panel with title "Candidate Patterns" and content:

> Phase 2 of the dashboard build. This view will surface:
>
> - Top behaviors with strongest booked-vs-not-booked differential, computed within call type
> - Pattern combinations (behaviors that co-occur in booked calls)
> - "Patterns considered and not yet supported by the data" -- including the rep_08 sequence that initially anchored the brief design
>
> Each candidate is labeled with confidence tier and an "at-scale" note: candidate findings would resolve at production volume within ~30-60 days of continuous scoring.

## Confidence label mapping (for the pills)

```js
const confidenceLabels = {
  confirmed: { text: "✓ Confirmed", color: "#10693e", bg: "#d4f4e0", desc: "N≥50 in each cell, signal robust at scale" },
  directional: { text: "→ Directional", color: "#7a4900", bg: "#fff3d4", desc: "10≤N<50, signal real but not yet causal" },
  candidate: { text: "? Candidate", color: "#6b4980", bg: "#f0e6f9", desc: "N<10, surface for tracking; would resolve at scale" },
  insufficient: { text: "⊘ Insufficient", color: "#777777", bg: "#eeeeee", desc: "N<5, cannot evaluate" }
};
```

Apply these consistently across all metrics in both views.

## Layout details

- Page max width: 1400px, centered
- Tab nav sticky at top
- Each view has 24px padding on the sides
- Section headings use a slightly larger font (1.25rem) with 16px bottom margin
- All numeric values render with appropriate precision (rates with 1 decimal; counts as integers)
- Bar charts have grid lines for readability; heatmap cells are 80px wide x 60px tall
- Filter chips on View 2 use rounded pill style; selected state has the accent color background

## Final touches

- A small "About" link at the bottom of every page that opens a modal explaining: "This is a prototype dashboard built from a 150-call sample. Production runs the same logic against live Snowflake data refreshing nightly. Confidence labels indicate sample-size-based reliability, not causal weight." Three short paragraphs total.

- Print-friendly CSS so the dashboard looks reasonable when printed (for stakeholder share-outs)

## What NOT to build in Phase 1

- Don't implement actual filter logic on View 1 (filters are UI placeholders that show toast messages)
- Don't implement View 3's content -- placeholder only
- Don't implement chart export, drill-down, or cross-view linking
- Don't implement live data refresh, websocket, or any backend connection
- Don't add fictional "feedback" buttons (👍/👎) on dashboard charts -- those belong on the brief, not the dashboard

Build it cleanly, ship it as a single HTML file, optimize for clarity over flash.


---

## Iteration 2 — Phase 1 revision

Applied six fixes to the Phase 1 build: sharpening AI insight copy, refining the heatmap color logic to use ratio-to-baseline rather than absolute rates, tightening the flagged-reps section, adjusting confidence label thresholds, and clarifying captions.

# Claude Code Prompt: Owner Dashboard — Phase 1 Revision

Apply six focused fixes to `owner_dashboard.html`. The existing file is at `[PATH TO]/owner_dashboard.html`. Read it first to preserve all existing structure, styling, and content. Output the updated file in place.

These are surgical revisions, not a rebuild. Don't restructure layouts or change anything not specified below.

---

## Fix 1: Headline stat card "5×" → "6×"

In Section 1.1 (Headline numbers strip), the third card currently shows "5×" with label "Spread between cold and confirmation booking rates."

**Change:** value from "5×" to "6×"

(Math: 77.8% / 12.7% = 6.13x. The AI insight panel below already says 6× correctly. Just aligning the card.)

---

## Fix 2: Heatmap color coding — ratio-based, not absolute-points

The current heatmap colors cells based on absolute distance from baseline (±10 pts). This works for high-baseline columns (50%+) but fails for cold outreach (12.7% baseline) — rep_08 at 19% is +6.3 pts absolute but 1.5× baseline relative, and currently shows as neutral when it should clearly show as above-baseline.

**Change to ratio-based logic:**

```js
function getCellColor(rate, baseline, n) {
  if (n === 0) return null; // empty cell
  const ratio = rate / baseline;
  let intensity = 'full'; // default

  // Pale tint for small samples
  if (n >= 1 && n < 5) intensity = 'pale';

  // Determine direction by ratio
  if (ratio >= 1.5) return { dir: 'above-strong', intensity };
  if (ratio >= 1.2) return { dir: 'above-light', intensity };
  if (ratio >= 0.8) return { dir: 'neutral', intensity };
  if (ratio >= 0.5) return { dir: 'below-light', intensity };
  return { dir: 'below-strong', intensity };
}
```

**Color mapping (use existing accent palette where possible):**

| Direction | Full intensity | Pale intensity (small N) |
|---|---|---|
| above-strong (≥1.5×) | strong green tint (e.g. #b8e5cc) | very light green (#e8f5ee) |
| above-light (1.2-1.5×) | light green (#d4f0de) | very light green (#eef8f1) |
| neutral (0.8-1.2×) | white/transparent | white/transparent |
| below-light (0.5-0.8×) | light red (#f5d4d4) | very light red (#faeeee) |
| below-strong (<0.5×) | strong red tint (#eba8a8) | light red (#f5d4d4) |

**Update the legend below the heatmap to reflect the new logic:**

Replace current legend ("Above baseline / Within ±10pts / Below baseline / Pale tint = small sample / No calls in this cell")

With:
- Strong above baseline (1.5× or more)
- Light above baseline (1.2-1.5×)
- Within ±20% of baseline
- Light below baseline (0.5-0.8×)
- Strong below baseline (less than 0.5×)
- Pale tint indicates small sample (n=1-4)
- Empty = no calls in this cell

**Also add a one-line caveat below the legend:**
> *Color is based on ratio to call-type baseline (rep's rate ÷ baseline rate), so a rep at 19% on a 12.7% baseline shows as above-baseline despite the small absolute number. Rep_08 books at 1.5× the cold-outreach baseline.*

---

## Fix 3: Drop "Other" row from headline chart

In Section 1.3, the booking-rate-by-call-type chart currently includes an "Other" row with n=3 calls at 66.7%. At n=3 this is misleading.

**Change:** remove the "Other" entry from `callTypeData`. The chart now shows 4 bars (Confirmation, In-flight follow-up, Inbound follow-up, Cold outreach).

The labels under the chart and the confidence pills should also drop the Other row.

The caveat text below stays as-is, but change "all five rows tighten within weeks" to "all four rows tighten within weeks."

---

## Fix 4: Group behaviors by call phase in View 2 table

Currently the behaviors table is sorted by differential (descending). Strong sort, but hard to scan as a coherent picture of the call. Add **phase grouping** on top of the sort.

**Phase groups (in this order):**

1. **Opening / Hook** — research_hook_used, referral_specificity, owner_name_used_in_opening, referral_used
2. **Discovery** — discovery_question_asked, rep_used_prospect_answer, prospect_language_mirrored, discovery_asked_*
3. **Pitch** — commission_math_specific, third_party_handling, google_visibility_angle_used, pos_integration_raised, social_proof_used
4. **Close** — specific_time_proposed, no_commitment_close_used, email_secured

**Implementation:**

- Render the table with a phase header row before each group: small uppercase label like "OPENING / HOOK" with a subtle background tint.
- Within each group, sort by differential descending (current behavior, just within-group).
- If a group has no rows for the current call type filter, skip the group header.
- The "sort by column" feature still works — when a user clicks a column header, sort flat across all groups (i.e., toggle off grouping when actively sorting).

Map for which field belongs to which phase (use this exact mapping):

```js
const fieldPhase = {
  research_hook_used: 'opening',
  referral_specificity: 'opening',
  referral_used: 'opening',
  owner_name_used_in_opening: 'opening',
  discovery_question_asked: 'discovery',
  rep_used_prospect_answer: 'discovery',
  prospect_language_mirrored: 'discovery',
  discovery_asked_order_source: 'discovery',
  discovery_asked_marketing: 'discovery',
  discovery_asked_priority: 'discovery',
  discovery_asked_other: 'discovery',
  commission_math_specific: 'pitch',
  third_party_handling: 'pitch',
  google_visibility_angle_used: 'pitch',
  pos_integration_raised: 'pitch',
  social_proof_used: 'pitch',
  no_commitment_close_used: 'close',
  specific_time_proposed: 'close',
  email_secured: 'close',
  pricing_disclosed_proactively: 'close',
  graceful_exit_on_rejection: 'close',
  tried_before_objection_handled: 'pitch'
};

const phaseLabels = {
  opening: 'Opening / Hook',
  discovery: 'Discovery',
  pitch: 'Pitch',
  close: 'Close'
};
```

Phase header row styling: small caps, light gray text, subtle row tint. Should look clearly distinct from data rows but not visually heavy.

---

## Fix 5: Replace verbatim phrases section with behavioral combinations

The current "Verbatim phrases from booked calls" section shows mostly call mechanics (`"give you a call"`, `"send you an email"`) — not insightful. Replace with a "Behavioral combinations" section that shows where co-occurrence of two behaviors is more predictive than either alone.

**New section title:** "Behavioral combinations" (replaces "Verbatim phrases from booked calls")

**Subtitle:** Cases where two behaviors firing together signals more than either alone.

**Content for cold_outreach filter:**

```js
const combinationsByCallType = {
  cold_outreach: [
    {
      label: "Adapted pitch + Mirrored language",
      desc: "Rep both adapted pitch content based on prospect's discovery answer (rep_used_prospect_answer = explicit or implicit) AND echoed prospect's specific phrasing (prospect_language_mirrored = exact_words or paraphrased).",
      booked_pct: 50,
      notbooked_pct: 19,
      diff: 31,
      n_booked_total: 10,
      n_notbooked_total: 69,
      confidence: "candidate",
      caveat: "Mirrored language almost always implies adapted pitch (mirroring without adapting is rare); reverse is not true. Combined behavior is a stronger signal than either alone."
    }
  ],
  inbound_followup: [
    {
      label: "Discovery before pitch + Specific time proposed",
      desc: "Rep asked open-ended question before pitching AND proposed a specific time (not open-ended) for follow-up.",
      booked_pct: 32,
      notbooked_pct: 5,
      diff: 27,
      n_booked_total: 19,
      n_notbooked_total: 20,
      confidence: "directional",
      caveat: "Both behaviors individually correlate with booking; the combination is consistent across booked calls in this sample."
    }
  ],
  in_flight_followup: [],
  confirmation: []
};
```

**Render each combination as a card or row showing:**
- Label (bold)
- Short description
- Booked %, not-booked %, differential (color-coded same as the main table)
- Confidence pill
- Sample size note

If the array for a call type is empty (in_flight, confirmation), render: "Combination analysis insufficient at current sample size for this call type."

**Caveat under section heading:**
> *Combinations surface where two behaviors firing together signals more than either alone. Production: continuous scoring evaluates combinations across all behavior pairs nightly; surfaced when combination differential exceeds individual differentials by 5+ points.*

---

## Fix 6: Add "Category" column to View 2 behaviors table

Add a new column to the behaviors table labeled "Category" that classifies each row as one of:

- **Differentiator** — booked rate ≥ 30% AND differential ≥ +15 pts
- **Possible differentiator** — differential ≥ +10 pts (but doesn't meet the booked-rate threshold)
- **Table stakes** — booked rate ≥ 50% AND not-booked rate ≥ 50% (high in both)
- **Inverse** — differential ≤ -10 pts
- **Weak / flat** — anything else

**Render as a small pill/tag** with these colors:

```js
const categoryStyles = {
  differentiator:           { text: 'Differentiator',           bg: '#d4f0de', color: '#10693e' },
  'possible differentiator':{ text: 'Possible differentiator',   bg: '#eef7f1', color: '#10693e' },
  'table stakes':           { text: 'Table stakes',              bg: '#eef0f3', color: '#444' },
  inverse:                  { text: 'Inverse',                   bg: '#f5d4d4', color: '#9a2c2c' },
  'weak / flat':            { text: 'Weak / flat',               bg: '#f3f3f3', color: '#777' }
};
```

**Where the Category column goes:** insert it between "Differential" and "N booked." So the column order becomes:

| Behavior | Value | Booked rate | Not-booked rate | Differential | **Category** | N booked | N not-booked | Confidence |

**Add a small caveat below the table:**
> *Category labels apply heuristic thresholds (Differentiator: booked ≥ 30%, diff ≥ +15pts; Table stakes: both ≥ 50%; Inverse: diff ≤ -10pts). At small samples, several behaviors fall into "weak / flat" not because they don't matter but because there isn't enough data to tell yet.*

---

## What NOT to change

- View 1's overall structure (cards, insight panel, headline chart, heatmap, flagged reps)
- View 2's filter pills, AI insight panel, sortable behavior table layout
- View 3 placeholder
- About modal
- Header, footer, tab nav
- Confidence label pills (✓ → ? ⊘) — these stay as-is
- Field tooltips on behavior names — keep them
- Any color choices other than the heatmap-specific ones above

---

## Output

Save updated file in place at `[PATH TO]/owner_dashboard.html`.

Print to stdout when done:
- "Fix 1 applied: 5× → 6×"
- "Fix 2 applied: heatmap ratio-based coloring"
- "Fix 3 applied: 'Other' row removed from headline chart"
- "Fix 4 applied: behaviors grouped by phase in View 2"
- "Fix 5 applied: phrases section replaced with combinations"
- "Fix 6 applied: Category column added to behavior table"

If any fix can't be applied (e.g., can't locate the relevant section), report which fix and stop — don't proceed with partial application.


---

## Iteration 3 — Phase 1 polish

Four polish fixes: rep tenure pills in the heatmap, total-call-count subtitles, the sticky tab nav adjustment, and refined caveat language.

# Claude Code Prompt: Owner Dashboard Phase 1 — Final Polish

Apply four focused fixes to `owner_dashboard.html`. The existing file is at `[PATH TO]/owner_dashboard.html`. Read it first to preserve all existing structure and content. Output the updated file in place.

These are surgical revisions, not a rebuild. Don't restructure layouts or change anything not specified below.

---

## Fix 1: Add tenure and call count to heatmap row labels

In View 1, Section 1.4 (rep × call type heatmap), the leftmost column currently shows just the rep ID (e.g., "rep_08"). Add tenure and total call count next to each rep ID for context.

**New row label format:**
```
rep_08
MID · 24 calls
```

Where:
- Rep ID stays bold (current style)
- Tenure label is uppercase, small, color-coded by tenure
- Total call count is the sum across all that rep's calls (across all call types in the dataset)

**Tenure colors:**
- Senior: `#10693e` (matches existing accent green)
- Mid: `#7a4900` (matches existing directional pill)
- New: `#6b4980` (matches existing candidate pill)

**Rep tenure and call count data (use exactly):**

```js
const repMeta = {
  "rep_01": { tenure: "senior", total: 7 },
  "rep_02": { tenure: "senior", total: 11 },
  "rep_03": { tenure: "senior", total: 19 },
  "rep_04": { tenure: "senior", total: 9 },
  "rep_05": { tenure: "senior", total: 4 },
  "rep_06": { tenure: "mid", total: 15 },
  "rep_07": { tenure: "mid", total: 11 },
  "rep_08": { tenure: "mid", total: 24 },
  "rep_09": { tenure: "mid", total: 10 },
  "rep_10": { tenure: "mid", total: 2 },
  "rep_11": { tenure: "new", total: 10 },
  "rep_12": { tenure: "new", total: 8 },
  "rep_13": { tenure: "new", total: 7 },
  "rep_14": { tenure: "new", total: 8 },
  "rep_15": { tenure: "new", total: 3 }
};
```

Visual: keep heatmap cell sizes the same; expand only the row label column width to accommodate tenure + count text below the rep ID. Two-line cell, with rep ID on top line and "TENURE · X calls" on second line in smaller text.

---

## Fix 2: Add call count distribution chart alongside booking rate

In View 1, Section 1.3 (Where bookings come from chart), add a companion volume chart **below** the existing booking rate chart.

**Title for the new chart:** "Call volume by call type"
**Chart type:** Horizontal bar chart matching the existing booking rate chart's style (same colors, same font, same sizing).

**Data:**
```js
const callVolumeData = [
  {label: "Cold outreach", n: 79},
  {label: "Inbound follow-up", n: 39},
  {label: "In-flight follow-up", n: 20},
  {label: "Confirmation", n: 9}
];
```

Note the order: descending by volume, NOT matching the booking rate chart's order (booking rate chart goes high-to-low by rate; this goes high-to-low by volume). This actually makes the comparison interesting -- the largest volume bucket (cold outreach) is the lowest rate, and vice versa. That's the visual story.

**Bar labels:** show the count and the percentage of total. E.g., "79 (53%)" for cold outreach.

**Caveat below the new chart:**
> *Cold outreach is the largest single bucket (53% of dials in this sample) AND has the lowest booking rate. Volume × rate is where leverage compounds — small execution improvements on cold outreach affect the most calls.*

**Section structure after this fix:**

Section 1.3 now contains:
1. Heading: "Where bookings come from — and where they don't"
2. Booking rate chart (existing)
3. Confidence pills row (existing)
4. Confidence caveat (existing)
5. **NEW:** Heading: "Call volume by call type" with subtle visual separation
6. **NEW:** Volume chart
7. **NEW:** Volume × rate caveat line

---

## Fix 3: Standardize value selection logic in View 2 behaviors table

Currently the cold outreach view shows one row per behavior field (the highest-differential value). The inbound view shows multiple rows per field (both positive and negative directions). This is inconsistent.

**Standardize to: show both the strongest positive AND strongest negative direction per field, if both meet a threshold.**

**Threshold for inclusion:**
- Positive direction: differential ≥ +10 pts
- Negative direction: differential ≤ -10 pts
- AND each row's booked rate or not-booked rate must be ≥ 15% (filters out very rare values)

**Updated data for cold_outreach (n=10 booked, 69 not-booked):**

```js
const behaviorTable_cold = [
  // OPENING / HOOK
  {field: "research_hook_used", value: "specific_findings", booked_rate: 60.0, nb_rate: 31.9, diff: 28.1, n_b: 10, n_nb: 69, confidence: "candidate"},
  {field: "referral_specificity", value: "detailed", booked_rate: 50.0, nb_rate: 30.4, diff: 19.6, n_b: 10, n_nb: 69, confidence: "candidate"},
  {field: "referral_specificity", value: "basic", booked_rate: 30.0, nb_rate: 49.3, diff: -19.3, n_b: 10, n_nb: 69, confidence: "candidate"},
  // DISCOVERY
  {field: "prospect_language_mirrored", value: "paraphrased", booked_rate: 50.0, nb_rate: 17.4, diff: 32.6, n_b: 10, n_nb: 69, confidence: "candidate"},
  {field: "prospect_language_mirrored", value: "not_mirrored", booked_rate: 40.0, nb_rate: 73.9, diff: -33.9, n_b: 10, n_nb: 69, confidence: "candidate"},
  {field: "rep_used_prospect_answer", value: "explicit", booked_rate: 30.0, nb_rate: 2.9, diff: 27.1, n_b: 10, n_nb: 69, confidence: "candidate"},
  {field: "rep_used_prospect_answer", value: "none", booked_rate: 20.0, nb_rate: 53.6, diff: -33.6, n_b: 10, n_nb: 69, confidence: "candidate"},
  {field: "discovery_question_asked", value: "before_pitch", booked_rate: 40.0, nb_rate: 26.1, diff: 13.9, n_b: 10, n_nb: 69, confidence: "candidate"},
  // PITCH
  {field: "third_party_handling", value: "proactive_reframe", booked_rate: 70.0, nb_rate: 46.4, diff: 23.6, n_b: 10, n_nb: 69, confidence: "candidate"},
  {field: "google_visibility_angle_used", value: "specific", booked_rate: 40.0, nb_rate: 15.9, diff: 24.1, n_b: 10, n_nb: 69, confidence: "candidate"},
  {field: "google_visibility_angle_used", value: "not_used", booked_rate: 30.0, nb_rate: 49.3, diff: -19.3, n_b: 10, n_nb: 69, confidence: "candidate"},
  {field: "commission_math_specific", value: "specific_dollars", booked_rate: 20.0, nb_rate: 1.4, diff: 18.6, n_b: 10, n_nb: 69, confidence: "candidate"},
  {field: "social_proof_used", value: "generic", booked_rate: 30.0, nb_rate: 18.8, diff: 11.2, n_b: 10, n_nb: 69, confidence: "candidate"},
  // CLOSE
  {field: "specific_time_proposed", value: "specific", booked_rate: 50.0, nb_rate: 17.4, diff: 32.6, n_b: 10, n_nb: 69, confidence: "candidate"},
  {field: "specific_time_proposed", value: "not_reached", booked_rate: 30.0, nb_rate: 53.6, diff: -23.6, n_b: 10, n_nb: 69, confidence: "candidate"}
];
```

**Updated data for inbound_followup (n=19 booked, 20 not-booked):**

```js
const behaviorTable_inbound = [
  // DISCOVERY
  {field: "discovery_question_asked", value: "before_pitch", booked_rate: 42.1, nb_rate: 15.0, diff: 27.1, n_b: 19, n_nb: 20, confidence: "directional"},
  {field: "discovery_question_asked", value: "none", booked_rate: 26.3, nb_rate: 45.0, diff: -18.7, n_b: 19, n_nb: 20, confidence: "directional"},
  {field: "rep_used_prospect_answer", value: "explicit", booked_rate: 21.1, nb_rate: 5.0, diff: 16.1, n_b: 19, n_nb: 20, confidence: "directional"},
  {field: "rep_used_prospect_answer", value: "none", booked_rate: 42.1, nb_rate: 65.0, diff: -22.9, n_b: 19, n_nb: 20, confidence: "directional"},
  {field: "prospect_language_mirrored", value: "paraphrased", booked_rate: 47.4, nb_rate: 35.0, diff: 12.4, n_b: 19, n_nb: 20, confidence: "directional"},
  {field: "prospect_language_mirrored", value: "not_mirrored", booked_rate: 47.4, nb_rate: 65.0, diff: -17.6, n_b: 19, n_nb: 20, confidence: "directional"},
  // CLOSE
  {field: "specific_time_proposed", value: "specific", booked_rate: 42.1, nb_rate: 15.0, diff: 27.1, n_b: 19, n_nb: 20, confidence: "directional"},
  {field: "specific_time_proposed", value: "not_reached", booked_rate: 15.8, nb_rate: 35.0, diff: -19.2, n_b: 19, n_nb: 20, confidence: "directional"}
];
```

The rest of the table rendering logic (phase grouping, category column, sort behavior) stays unchanged. Just the source data is updated.

---

## Fix 4: Drop the Behavioral combinations section

Remove the entire "Behavioral combinations" section from View 2. This includes:
- The section heading
- The subtitle/caveat text
- The combinations card(s)
- The `combinationsByCallType` constant in the JS (can be deleted entirely)
- Any rendering function specific to combinations (e.g., `renderCombinations()`)

The section was thin (only one or two combinations to show at this sample size), and the "adapted + mirrored" insight is already captured in the AI insight panel for cold outreach.

After removal, View 2's structure becomes:
1. Filter pills (call type)
2. AI insight panel
3. Behaviors table
4. (END — phrase frequency was already removed; combinations now removed too)

The footer ("About") should appear directly after the behaviors table.

---

## What NOT to change

- Tab nav, header, footer, About modal
- View 1's headline stat cards, AI insight panel, flagged reps section
- View 2's filter pills, AI insight panel, behavior table grouping/category column/sort
- View 3 placeholder
- Confidence label pills, field tooltips, color schemes (other than what's specified above)

---

## Output

Save updated file in place at `[PATH TO]/owner_dashboard.html`.

Print to stdout when done:
- "Fix 1 applied: tenure + call count added to heatmap rep labels"
- "Fix 2 applied: call volume chart added below booking rate chart"
- "Fix 3 applied: behavior table values standardized (positive + negative directions per field)"
- "Fix 4 applied: behavioral combinations section removed"

If any fix can't be applied (e.g., can't locate the relevant section), report which fix and stop — don't proceed with partial application.


---

## Iteration 4 — Combined fixes

Three substantive changes: combined the booking rate chart and call volume chart into a single visualization (one bar = booking rate, side label = volume); de-duplicated the behavior table by removing redundant negative-direction rows and adding asymmetric "absence" sub-lines; added a methodology note above the behavior table.

# Claude Code Prompt: Owner Dashboard — Two Surgical Fixes

Apply two focused fixes to `owner_dashboard.html`. The existing file is at `[PATH TO]/owner_dashboard.html`. Read it first to preserve all existing structure and content. Output the updated file in place.

These are surgical revisions, not a rebuild. Don't restructure layouts or change anything not specified below.

---

## Fix 1: Combine booking rate and call volume into a single chart

In View 1, Section 1.3, the booking rate chart and the call volume chart are currently separate. Combine them into a single chart.

**Approach:** A single horizontal bar chart where:
- Bar length represents booking rate (the existing chart's data)
- Each bar has the call volume rendered as a label on the right side, formatted: `· 79 calls (53% of dials)`
- Bars are ordered by **call volume descending** (cold outreach on top, confirmation at bottom). This tells the "biggest bucket, lowest rate" story.

**Updated heading:** "Where bookings come from — and at what volume"

**Updated subtitle (small italic line below the chart heading):** "Bar length = booking rate. Volume per call type shown alongside each bar."

**Bar structure example (visual):**

```
Cold outreach    [████░░░░░░] 12.7%   · 79 calls (53% of dials)
Inbound followup [██████░░░░] 48.7%   · 39 calls (26%)
In-flight followup [███████░░] 65.0%   · 20 calls (13%)
Confirmation     [████████░░] 77.8%   · 9 calls (6%)
```

**Data — replace the existing `callTypeData` and `callVolumeData` constants with a single combined data structure:**

```js
const callTypeChartData = [
  {label: "Cold outreach", n: 79, booked: 10, rate: 12.7, pct_of_total: 53, confidence: "directional"},
  {label: "Inbound follow-up", n: 39, booked: 19, rate: 48.7, pct_of_total: 26, confidence: "directional"},
  {label: "In-flight follow-up", n: 20, booked: 13, rate: 65.0, pct_of_total: 13, confidence: "directional"},
  {label: "Confirmation", n: 9, booked: 7, rate: 77.8, pct_of_total: 6, confidence: "candidate"}
];
```

**Implementation notes:**
- Use Chart.js horizontal bar chart with rate as the value
- Render the volume label as part of the bar label (Chart.js plugin `chartjs-plugin-datalabels` may help, OR render volume labels as DOM elements next to the chart canvas)
- Keep the confidence pills row below the chart
- Keep the existing caveat about confidence at scale
- Add a new caveat below the chart specifically about volume × rate:

> *Cold outreach is the largest single bucket (53% of dials in this sample) AND has the lowest booking rate. Volume × rate is where leverage compounds — small execution improvements on cold outreach affect the most calls.*

**Remove:**
- The standalone "Call volume by call type" chart heading and chart
- The `callVolumeData` constant (data is now in the unified `callTypeChartData`)
- Any rendering function specific to the standalone volume chart

---

## Fix 2: De-duplicate behavior table in View 2

The behavior table currently shows multiple rows per field — one for the positive direction, one for the negative direction. This is mostly redundant because the Category column already conveys whether a behavior is a Differentiator (presence helps, absence hurts) or Inverse (presence hurts).

### 2.1 Default behavior: one row per field

Show only the positive-direction row per field. The Category column conveys whether the behavior is a Differentiator / Possible differentiator / Inverse / Table stakes / Weak.

**Updated cold outreach data — REPLACES the current `behaviorTable_cold` constant entirely:**

```js
const behaviorTable_cold = [
  // OPENING / HOOK
  {field: "research_hook_used", value: "specific_findings", booked_rate: 60.0, nb_rate: 31.9, diff: 28.1, n_b: 10, n_nb: 69, confidence: "candidate", absence_note: null},
  {field: "referral_specificity", value: "detailed", booked_rate: 50.0, nb_rate: 30.4, diff: 19.6, n_b: 10, n_nb: 69, confidence: "candidate", absence_note: null},
  // DISCOVERY
  {field: "prospect_language_mirrored", value: "paraphrased", booked_rate: 50.0, nb_rate: 17.4, diff: 32.6, n_b: 10, n_nb: 69, confidence: "candidate", absence_note: "Absence (not_mirrored) appears in 73.9% of not-booked vs 40% of booked — the gap is symmetric on both ends."},
  {field: "rep_used_prospect_answer", value: "explicit", booked_rate: 30.0, nb_rate: 2.9, diff: 27.1, n_b: 10, n_nb: 69, confidence: "candidate", absence_note: "Absence (none) appears in 53.6% of not-booked vs 20% of booked — both ends carry signal."},
  {field: "discovery_question_asked", value: "before_pitch", booked_rate: 40.0, nb_rate: 26.1, diff: 13.9, n_b: 10, n_nb: 69, confidence: "candidate", absence_note: null},
  // PITCH
  {field: "third_party_handling", value: "proactive_reframe", booked_rate: 70.0, nb_rate: 46.4, diff: 23.6, n_b: 10, n_nb: 69, confidence: "candidate", absence_note: null},
  {field: "google_visibility_angle_used", value: "specific", booked_rate: 40.0, nb_rate: 15.9, diff: 24.1, n_b: 10, n_nb: 69, confidence: "candidate", absence_note: "Absence (not_used) appears in 49.3% of not-booked vs 30% of booked."},
  {field: "commission_math_specific", value: "specific_dollars", booked_rate: 20.0, nb_rate: 1.4, diff: 18.6, n_b: 10, n_nb: 69, confidence: "candidate", absence_note: null},
  {field: "social_proof_used", value: "generic", booked_rate: 30.0, nb_rate: 18.8, diff: 11.2, n_b: 10, n_nb: 69, confidence: "candidate", absence_note: null},
  {field: "pos_integration_raised", value: "reactive", booked_rate: 40.0, nb_rate: 26.1, diff: 13.9, n_b: 10, n_nb: 69, confidence: "candidate", absence_note: null},
  // CLOSE
  {field: "specific_time_proposed", value: "specific", booked_rate: 50.0, nb_rate: 17.4, diff: 32.6, n_b: 10, n_nb: 69, confidence: "candidate", absence_note: "Absence (not_reached, i.e., call ended before close) appears in 53.6% of not-booked vs 30% of booked."}
];
```

**Updated inbound followup data — REPLACES the current `behaviorTable_inbound` constant entirely:**

```js
const behaviorTable_inbound = [
  // DISCOVERY
  {field: "discovery_question_asked", value: "before_pitch", booked_rate: 42.1, nb_rate: 15.0, diff: 27.1, n_b: 19, n_nb: 20, confidence: "directional", absence_note: "Absence (none) appears in 45% of not-booked vs 26.3% of booked."},
  {field: "rep_used_prospect_answer", value: "explicit", booked_rate: 21.1, nb_rate: 5.0, diff: 16.1, n_b: 19, n_nb: 20, confidence: "directional", absence_note: "Absence (none) appears in 65% of not-booked vs 42.1% of booked — strongest absence signal in this view."},
  {field: "prospect_language_mirrored", value: "paraphrased", booked_rate: 47.4, nb_rate: 35.0, diff: 12.4, n_b: 19, n_nb: 20, confidence: "directional", absence_note: "Absence (not_mirrored) appears in 65% of not-booked vs 47.4% of booked."},
  // CLOSE
  {field: "specific_time_proposed", value: "specific", booked_rate: 42.1, nb_rate: 15.0, diff: 27.1, n_b: 19, n_nb: 20, confidence: "directional", absence_note: "Absence (not_reached) appears in 35% of not-booked vs 15.8% of booked."}
];
```

### 2.2 Render the absence_note as a sub-line under the row

When `absence_note` is present (not null), render it as a small italic sub-line directly below the row, indented under the Behavior column.

**Visual treatment:**
- Italic, smaller font (about 0.85x the row text)
- Soft text color (e.g., `var(--text-soft)`)
- Indented slightly (left padding ~16-20px)
- Prefixed with a small unicode arrow or symbol: `↳`
- The sub-line spans across what would be the Behavior column in width — it's a continuation, not a new row in the table semantics

**Implementation note:** in HTML, this can be a second row in the table with `colspan` covering all columns, with a class like `behavior-sub-row`. CSS hides default cell borders on the sub-row to make it visually attached to the row above.

When `absence_note` is null, no sub-line is rendered.

### 2.3 Update the table caveat below

Replace the existing caveat below the behaviors table with:

> *Each row shows the strongest direction per behavior; absence notes call out where the behavior's absence carries an asymmetric or independent signal worth coaching toward. Category labels apply heuristic thresholds (Differentiator: booked ≥ 30%, diff ≥ +15pts; Table stakes: both ≥ 50%; Inverse: diff ≤ -10pts). At small samples, several behaviors fall into "weak / flat" not because they don't matter but because there isn't enough data to tell yet.*

---

## Fix 3: Add methodology note above the behavior table

The current behavior table doesn't explain WHY these specific behaviors appear vs. the 23 total fields in the scoring schema. Add a small methodology note directly above the behavior table in View 2 -- after the AI insight panel, before the table heading.

**New element: small collapsible note (or always-visible italic line) titled "How these behaviors were selected":**

> *Behaviors shown have absolute differential ≥ 10pts AND base rate ≥ 15% in at least one group (booked or not-booked). Some behaviors meeting these thresholds are excluded if they're redundant with another row (e.g., binary inverses where the Category column already conveys the absence) or too rare to interpret reliably. The production version evaluates all 23 behaviors in the scoring schema nightly; rows surface based on continuous-significance tests at scale rather than fixed thresholds.*

Visual treatment: small italic text in `var(--text-soft)`, with a subtle `(i)` icon prefix or a small expand/collapse toggle. If using a toggle, default to collapsed with a one-line summary visible: "How these behaviors were selected →" that expands on click.

I lean toward always-visible italic line (no toggle) since the audience is managers who benefit from transparency over UI minimalism. Designer's call — pick whichever fits the existing visual language.

Place between the AI insight panel and the "Behaviors associated with booked calls" heading.

---

## What NOT to change

- Tab nav, header, footer, About modal
- View 1's headline stat cards, AI insight panel, heatmap, flagged reps section
- View 2's filter pills, AI insight panel, behavior table grouping (Opening / Discovery / Pitch / Close), Category column, sort behavior, field tooltips
- View 3 placeholder
- Confidence label pills, color schemes (other than what's specified above)
- Any data outside the two constants being replaced

---

## Output

Save updated file in place at `[PATH TO]/owner_dashboard.html`.

Print to stdout when done:
- "Fix 1 applied: booking rate and call volume combined into single chart"
- "Fix 2 applied: behavior table de-duplicated; absence notes added inline where signal is asymmetric"
- "Fix 3 applied: methodology note added above behavior table"

If any fix can't be applied (e.g., can't locate the relevant section), report which fix and stop — don't proceed with partial application.


---

## Iteration 5 — Final polish (seven fixes)

Seven coordinated changes: renamed views to action-oriented labels (Call outcomes / Behavior insights / Coaching opportunities); added an "Overall" reference column to the heatmap with no color coding; reordered call type columns to match View 2 (Cold → Demo confirmation); made the heatmap header sticky during page scroll; added a View 2 toggle for showing the full category landscape (table stakes, weak, inverse) inline; removed absence sub-lines (Category column conveys the same information more cleanly); added call volume to filter pill labels.

# Claude Code Prompt: Owner Dashboard — Final Consolidated Fixes

Apply seven focused fixes to `owner_dashboard.html`. The existing file is at `[PATH TO]/owner_dashboard.html`. Read it first to preserve all existing structure and content. Output the updated file in place.

These are surgical revisions, not a rebuild. Don't restructure layouts or change anything not specified below.

---

## Fix 1: Rename views

Update the tab nav and any view-heading references throughout the file to use new names:

| Old name | New name |
|---|---|
| View 1 · Performance & Flagging | View 1 · Call outcomes |
| View 2 · What's Working | View 2 · Behavior insights |
| View 3 · Candidate Patterns | View 3 · Coaching opportunities |

Update everywhere these appear:
- Tab nav links
- View headings (if present at the top of each view)
- Internal references in placeholder text (e.g., "Investigate via View 3 once Phase 2 is deployed" should say "Investigate via View 3 (Coaching opportunities) once Phase 2 is deployed")
- Any other occurrence of the old names

The View 3 placeholder body text should also be updated to reflect the new framing:

> Phase 2 of the dashboard build. View 3 is where managers turn signal into action. Two sections:
>
> 1. **Patterns under consideration.** Candidate behaviors with strongest differentials, surfaced from View 2. Managers review and promote patterns to "best practice" status — promoted patterns flow into the rep prep tool as suggested coaching points.
>
> 2. **Rep adherence to promoted patterns.** For each rep, how often they execute each promoted behavior. Surfaces specific coaching opportunities (e.g., rep_07 at 0% on third-party reframe, a confirmed differentiator).
>
> View 3 closes the loop between dashboard analytics and rep-facing tooling. The dashboard isn't just diagnostic — it's where managers make the call on which patterns become organizational practice.

---

## Fix 2: Add "Overall" column to heatmap, reorder columns, add overall rate to row labels

### 2.1 Reorder existing call type columns

Current order: Confirmation | In-flight follow-up | Inbound follow-up | Cold outreach

**New order (matches View 2 filter pill order, leading with the most actionable call type):**
**Cold outreach | Inbound follow-up | In-flight follow-up | Confirmation**

Update column headers and the data rendering loop to match.

### 2.2 Add a leftmost "Overall" column

Insert a new column to the LEFT of all call type columns, labeled "Overall."

For each rep, this column shows the rep's aggregate booking rate across ALL their calls. Sample data:

```js
const repOverall = {
  "rep_01": {n: 7, booked: 7, rate: 100.0},
  "rep_02": {n: 11, booked: 4, rate: 36.4},
  "rep_03": {n: 19, booked: 4, rate: 21.1},
  "rep_04": {n: 9, booked: 1, rate: 11.1},
  "rep_05": {n: 4, booked: 2, rate: 50.0},
  "rep_06": {n: 15, booked: 3, rate: 20.0},
  "rep_07": {n: 11, booked: 1, rate: 9.1},
  "rep_08": {n: 24, booked: 6, rate: 25.0},
  "rep_09": {n: 10, booked: 8, rate: 80.0},
  "rep_10": {n: 2, booked: 2, rate: 100.0},
  "rep_11": {n: 10, booked: 4, rate: 40.0},
  "rep_12": {n: 8, booked: 5, rate: 62.5},
  "rep_13": {n: 7, booked: 1, rate: 14.3},
  "rep_14": {n: 8, booked: 0, rate: 0.0},
  "rep_15": {n: 3, booked: 1, rate: 33.3}
};
```

Cells render the rate (e.g., "25%") with a small "n=24 · 6 booked" sub-line, same format as other heatmap cells.

**Important: NO color coding on the Overall column.** The Overall column is reference-only — it provides context but the manager shouldn't read it as a performance signal (because of the call-mix problem the rest of the dashboard exists to solve). Use neutral white/light gray background for ALL Overall cells regardless of value.

**Visual distinction:** the Overall column header should be visually subtle — slightly muted text color, lighter background tint, smaller font weight than the other column headers. The cells should have a subtle vertical divider on the right edge to separate them from the call type columns. Make it clear at a glance that Overall is reference, not the same kind of comparison the other columns show.

The "baseline 77.8%" / "baseline 65%" / etc. subtitle that appears under each call type column header should NOT appear under the Overall column. Instead, render small gray text: "all calls"

### 2.3 Update the heatmap caveat below

Currently the caveat says: "Color is based on ratio to call-type baseline (rep's rate ÷ baseline rate), so a rep at 19% on a 12.7% baseline shows as above-baseline despite the small absolute number. Rep_08 books at 1.5× the cold-outreach baseline."

Replace with:

> *Color coding compares rep performance to the call-type baseline within each call type column. A rep at 19% on a 12.7% baseline shows as above-baseline despite the small absolute number — rep_08 books at 1.5× the cold-outreach baseline. The Overall column is reference only and is intentionally not color-coded, because raw aggregate rates conflate behavioral performance with call mix.*

---

## Fix 3: Sticky heatmap header

The current heatmap is too tall to view headers and rep rows simultaneously without scrolling. Make the heatmap column header row sticky during scroll within the heatmap section.

Implementation: use CSS `position: sticky; top: 0` on the column header row. The heatmap container should have `overflow: visible` with the header sticky relative to the page scroll.

If the page already has a sticky tab nav at the top, the heatmap header should stick BELOW the tab nav (use `top: [tab-nav-height]px`) so they don't overlap. Determine the tab nav height from the existing CSS and offset accordingly.

The header row should have a solid background (white or near-white) and a subtle drop shadow when stuck, so it visually separates from the rows scrolling beneath it.

---

## Fix 4: View 2 — restore full Category landscape with toggle

Currently the View 2 behaviors table only shows behaviors meeting "Differentiator" or "Possible differentiator" thresholds. Add a toggle that expands the view to show all categories (Table stakes, Inverse, Weak) inline within their phase groups.

### 4.1 Toggle UI

Add a toggle switch above the behaviors table, to the right of the table heading. Visual style: small switch with label "Show all categories" (off by default).

When toggled OFF (default):
- Table shows only rows where Category is "Differentiator" or "Possible differentiator"
- Behaves as it currently does

When toggled ON:
- Table shows all rows that meet base thresholds (differential ≥ ±10pts AND base rate ≥ 15% in either group)
- Categories are NOT separated into a sub-section — they appear inline within their phase group, sorted by absolute differential descending
- A Discovery group might contain: Differentiator row → Possible differentiator row → Table stakes row → Inverse row → Weak row, all under one "Discovery" phase header

### 4.2 New data — full landscape including Table stakes, Inverse, Weak

For cold outreach (n=10 booked, 69 not-booked), expand `behaviorTable_cold` to include the full landscape:

```js
const behaviorTable_cold = [
  // OPENING / HOOK
  {field: "research_hook_used", value: "specific_findings", booked_rate: 60.0, nb_rate: 31.9, diff: 28.1, n_b: 10, n_nb: 69, confidence: "candidate", category: "differentiator"},
  {field: "referral_specificity", value: "detailed", booked_rate: 50.0, nb_rate: 30.4, diff: 19.6, n_b: 10, n_nb: 69, confidence: "candidate", category: "differentiator"},
  {field: "referral_used", value: "True", booked_rate: 90.0, nb_rate: 92.8, diff: -2.8, n_b: 10, n_nb: 69, confidence: "candidate", category: "table stakes"},
  {field: "owner_name_used_in_opening", value: "True", booked_rate: 40.0, nb_rate: 47.8, diff: -7.8, n_b: 10, n_nb: 69, confidence: "candidate", category: "weak / flat"},
  // DISCOVERY
  {field: "prospect_language_mirrored", value: "paraphrased", booked_rate: 50.0, nb_rate: 17.4, diff: 32.6, n_b: 10, n_nb: 69, confidence: "candidate", category: "differentiator"},
  {field: "rep_used_prospect_answer", value: "explicit", booked_rate: 30.0, nb_rate: 2.9, diff: 27.1, n_b: 10, n_nb: 69, confidence: "candidate", category: "differentiator"},
  {field: "discovery_question_asked", value: "before_pitch", booked_rate: 40.0, nb_rate: 26.1, diff: 13.9, n_b: 10, n_nb: 69, confidence: "candidate", category: "possible differentiator"},
  {field: "discovery_question_asked", value: "after_pitch", booked_rate: 40.0, nb_rate: 46.4, diff: -6.4, n_b: 10, n_nb: 69, confidence: "candidate", category: "weak / flat"},
  // PITCH
  {field: "third_party_handling", value: "proactive_reframe", booked_rate: 70.0, nb_rate: 46.4, diff: 23.6, n_b: 10, n_nb: 69, confidence: "candidate", category: "differentiator"},
  {field: "google_visibility_angle_used", value: "specific", booked_rate: 40.0, nb_rate: 15.9, diff: 24.1, n_b: 10, n_nb: 69, confidence: "candidate", category: "differentiator"},
  {field: "commission_math_specific", value: "specific_dollars", booked_rate: 20.0, nb_rate: 1.4, diff: 18.6, n_b: 10, n_nb: 69, confidence: "candidate", category: "possible differentiator"},
  {field: "social_proof_used", value: "generic", booked_rate: 30.0, nb_rate: 18.8, diff: 11.2, n_b: 10, n_nb: 69, confidence: "candidate", category: "possible differentiator"},
  {field: "pos_integration_raised", value: "reactive", booked_rate: 40.0, nb_rate: 26.1, diff: 13.9, n_b: 10, n_nb: 69, confidence: "candidate", category: "possible differentiator"},
  {field: "pos_integration_raised", value: "not_applicable", booked_rate: 50.0, nb_rate: 50.7, diff: -0.7, n_b: 10, n_nb: 69, confidence: "candidate", category: "table stakes"},
  {field: "commission_math_specific", value: "generic", booked_rate: 40.0, nb_rate: 46.4, diff: -6.4, n_b: 10, n_nb: 69, confidence: "candidate", category: "weak / flat"},
  // CLOSE
  {field: "specific_time_proposed", value: "specific", booked_rate: 50.0, nb_rate: 17.4, diff: 32.6, n_b: 10, n_nb: 69, confidence: "candidate", category: "differentiator"},
  {field: "no_commitment_close_used", value: "True", booked_rate: 20.0, nb_rate: 15.9, diff: 4.1, n_b: 10, n_nb: 69, confidence: "candidate", category: "weak / flat"}
];
```

For inbound followup (n=19 booked, 20 not-booked):

```js
const behaviorTable_inbound = [
  // DISCOVERY
  {field: "discovery_question_asked", value: "before_pitch", booked_rate: 42.1, nb_rate: 15.0, diff: 27.1, n_b: 19, n_nb: 20, confidence: "directional", category: "differentiator"},
  {field: "rep_used_prospect_answer", value: "explicit", booked_rate: 21.1, nb_rate: 5.0, diff: 16.1, n_b: 19, n_nb: 20, confidence: "directional", category: "possible differentiator"},
  {field: "prospect_language_mirrored", value: "paraphrased", booked_rate: 47.4, nb_rate: 35.0, diff: 12.4, n_b: 19, n_nb: 20, confidence: "directional", category: "possible differentiator"},
  {field: "referral_used", value: "False", booked_rate: 89.5, nb_rate: 75.0, diff: 14.5, n_b: 19, n_nb: 20, confidence: "directional", category: "table stakes"},
  // CLOSE
  {field: "specific_time_proposed", value: "specific", booked_rate: 42.1, nb_rate: 15.0, diff: 27.1, n_b: 19, n_nb: 20, confidence: "directional", category: "differentiator"}
];
```

(Note: inbound has fewer rows because we removed the redundant negative-direction rows in the prior fix; here we expand only with table stakes / weak rows that genuinely add information.)

### 4.3 Render logic

When the toggle is OFF, filter the array to include only Differentiator and Possible differentiator rows, then group by phase as currently.

When the toggle is ON, include all rows, group by phase, sort by absolute differential descending within each phase group.

Phase groupings stay as currently mapped (`research_hook_used` → opening, etc.).

---

## Fix 5: Drop absence sub-lines

Remove all `absence_note` sub-lines under behavior table rows. Remove the `absence_note` field from the behavior table data structures (it's no longer used).

The Category column now conveys the relationship between presence and absence — Differentiator implies absence is also a coaching point. The asymmetric signal information lives in the production-version drill-down, not in the headline view.

Update the table caveat to remove any reference to absence notes:

> *Each row shows the strongest direction per behavior. Category labels apply heuristic thresholds (Differentiator: booked ≥ 30%, diff ≥ +15pts; Table stakes: both ≥ 50%; Inverse: diff ≤ -10pts; Weak / flat: differential below ±10pts). Toggle "Show all categories" to see Table stakes, Weak, and Inverse rows alongside differentiators.*

---

## Fix 6: Add call volume to View 2 filter pills

Update the call type filter pill labels to include call count and percentage of total dials:

| Old label | New label |
|---|---|
| Cold outreach | Cold outreach (n=79, 53%) |
| Inbound follow-up | Inbound follow-up (n=39, 26%) |
| In-flight follow-up (limited data) | In-flight follow-up (n=20, 13%) |
| Confirmation (limited data) | Confirmation (n=9, 6%) |

The "(limited data)" qualifier can be dropped since the count makes the data thinness self-evident.

---

## Fix 7: Add methodology note above behavior table

Add a small italic line above the behaviors table heading in View 2 (after the AI insight panel, before the table). This was specified in the prior fix prompt but didn't land. Reapply now.

> *How these behaviors are selected: behaviors shown have absolute differential ≥ 10pts AND base rate ≥ 15% in at least one group (booked or not-booked). Production version evaluates all 23 behaviors in the scoring schema nightly and surfaces rows based on continuous-significance tests at scale rather than fixed thresholds.*

Visual treatment: small italic text in `var(--text-soft)`, with a subtle `(i)` icon prefix. Always-visible (no expand/collapse). Place between the AI insight panel and the "Behaviors associated with booked calls" heading.

---

## What NOT to change

- About modal, footer
- View 1 headline stat cards, AI insight panel, combined booking rate + volume chart, flagged reps section
- View 2 AI insight panel, sort behavior on column headers, field tooltips, confidence pills
- View 3 placeholder layout (only the body text changes per Fix 1)
- Confidence label conventions, color schemes (other than what's specified above)
- Any Phase 2 functionality (this is Phase 1 polish only)

---

## Output

Save updated file in place at `[PATH TO]/owner_dashboard.html`.

Print to stdout when done:
- "Fix 1 applied: views renamed (Call outcomes / Behavior insights / Coaching opportunities)"
- "Fix 2 applied: Overall column added to heatmap, columns reordered to match View 2"
- "Fix 3 applied: heatmap header is sticky during scroll"
- "Fix 4 applied: View 2 toggle for full category landscape"
- "Fix 5 applied: absence sub-lines removed"
- "Fix 6 applied: call volume added to View 2 filter pills"
- "Fix 7 applied: methodology note added above behavior table"

If any fix can't be applied, report which fix and stop — don't proceed with partial application.


---

## Iteration 6 — Sticky header fix

Single-line CSS fix. The previous iteration's sticky header didn't actually pin during page scroll because `.heatmap` had `overflow-x: auto` which created a scrolling context that captured the sticky positioning. Removing `overflow-x: auto` allowed the sticky to attach to the page scroll properly.

# Claude Code Prompt: Fix Sticky Heatmap Header

One-line CSS fix to `owner_dashboard.html` at `[PATH TO]/owner_dashboard.html`.

## The bug

The `.heatmap` container has `overflow-x: auto`, which creates a new scrolling context. This means `position: sticky` on `.heatmap thead th` only works relative to the heatmap container — not relative to the page scroll. When a user scrolls the page, the column headers scroll away with the rest of the heatmap instead of staying pinned to the top of the viewport.

## The fix

In the `.heatmap` CSS rule, remove `overflow-x: auto`. With 5 columns (Overall + 4 call types) and the existing fixed column widths, the table fits comfortably within the page width — horizontal overflow handling isn't needed.

**Find this rule:**

```css
.heatmap {
  overflow-x: auto;
  background: white;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 18px;
}
```

**Replace with:**

```css
.heatmap {
  background: white;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 18px;
}
```

That's it. The `position: sticky; top: 128px` on `.heatmap thead th` will then attach to the page scroll context and work correctly.

## Verify after the fix

The sticky header should now pin to the top of the viewport (128px down from the top, beneath the tab nav) when the user scrolls past it. Column headers (Overall, Cold outreach, Inbound follow-up, In-flight follow-up, Confirmation) and their baseline subtitles should stay visible while scrolling through rep rows.

## Output

Save updated file in place at `[PATH TO]/owner_dashboard.html`.

Print to stdout: "Sticky heatmap header fixed: removed overflow-x:auto from .heatmap container."

If the rule can't be located, report and stop.


---

## Iteration 7 — Call type rename and tooltips

Final rename pass: display labels updated to "Cold outreach / Inbound leads / Re-engagement / Demo confirmation" while keeping underlying data keys unchanged (so all data structures still use cold_outreach, inbound_followup, in_flight_followup, confirmation). Added (i) tooltip icons next to call type labels in the headline chart, heatmap column headers, and View 2 filter pills. Tooltip content explains each call type situationally and notes that inbound_followup and in_flight_followup are categories created via the situational classifier rather than fields in Owner's source data.

# Claude Code Prompt: Dashboard — Call Type Rename + Tooltips

Apply two related fixes to `owner_dashboard.html` at `[PATH TO]/owner_dashboard.html`. Read the file first, preserve all existing structure and content. Output the updated file in place.

## Fix 1: Rename call type display labels

Replace the display labels for call types throughout the dashboard. Underlying data keys stay the same — only the user-facing display strings change.

| Underlying key | Old display label | New display label |
|---|---|---|
| `cold_outreach` | Cold outreach | Cold outreach (no change) |
| `inbound_followup` | Inbound follow-up | Inbound leads |
| `in_flight_followup` | In-flight follow-up | Re-engagement |
| `confirmation` | Confirmation | Demo confirmation |
| `other` | Other | Other (no change) |

**Important:** keep all underlying data keys (`inbound_followup`, `in_flight_followup`, `confirmation`) unchanged in the JS data structures. Only the *display strings* shown to users change. This preserves data integrity without rewriting object keys throughout the file.

There's likely a `callTypeDisplay` map (or similar) used to render labels. Update that map. If labels are inlined in HTML strings (chart axis labels, filter pill text, headers, captions), update those too.

**Specific places to update:**

1. **View 1 headline chart bar labels** — "Inbound follow-up" becomes "Inbound leads"; "In-flight follow-up" becomes "Re-engagement"; "Confirmation" becomes "Demo confirmation"
2. **View 1 confidence pills row below the chart** — same labels updated
3. **View 1 heatmap column headers** — "Inbound follow-up" → "Inbound leads"; "In-flight follow-up" → "Re-engagement"; "Confirmation" → "Demo confirmation"
4. **View 1 reps to flag cards** — wherever a flagged rep's call type is displayed, use the new label
5. **View 1 AI insight panel text** — update mentions of the call types (e.g., "rep_01's 100% rate reflects an in-flight follow-up queue (65% baseline)" becomes "...a re-engagement queue (65% baseline)")
6. **View 2 filter pills** — "Inbound follow-up (n=39, 26%)" becomes "Inbound leads (n=39, 26%)"; "In-flight follow-up (n=20, 13%)" becomes "Re-engagement (n=20, 13%)"; "Confirmation (n=9, 6%)" becomes "Demo confirmation (n=9, 6%)"
7. **View 2 AI insight panel headers** — e.g., "What's working in cold outreach" stays, "What's working in inbound follow-up" becomes "What's working in inbound leads"; "What's working in in-flight follow-up" becomes "What's working in re-engagement"
8. **AI insight body text** — anywhere the call types are mentioned in narrative paragraphs, update labels
9. **View 3 placeholder text** — if any call type mentions, update
10. **About modal** — if it mentions call types
11. **Heatmap baseline subtitles** ("baseline 48.7%" etc.) — these stay tied to the renamed columns

Do a thorough search across the file for `Inbound follow-up`, `In-flight follow-up`, `inbound follow-up`, `in-flight follow-up`, `Confirmation` (capitalized standalone, not as part of a longer phrase like "confirmation pill"), and replace per the table above.

## Fix 2: Add (i) tooltip icons next to call type labels

Add a small `(i)` icon next to each call type label in three locations. On hover, the icon reveals a tooltip with the definition.

### Tooltip content

```js
const callTypeDefinitions = {
  cold_outreach: "Outbound dial to a prospect with no prior contact. The rep is starting the relationship from scratch.",
  inbound_followup: "Prospect raised their hand first via form fill, request, or referral. This is the first sales conversation. (Note: this category was created via situational classifier on call transcripts; it doesn't exist in the source data taxonomy.)",
  in_flight_followup: "A prior conversation already happened — typically a 'try me next week' callback or continued thread from a previous call. The rep is re-engaging an existing thread, not starting fresh. (Note: this category was created via situational classifier on call transcripts; it doesn't exist in the source data taxonomy.)",
  confirmation: "A demo is already scheduled. The call is to confirm details, send the calendar invite, or handle logistics."
};
```

### Where the (i) icons go

Three locations:

**1. View 1 headline chart**
Next to each call type name in the bar chart labels OR in the confidence pills row below the chart (designer's call — wherever fits cleanly without crowding the chart). Render as a small superscript `ⓘ` or `(i)` after the label.

**2. View 1 heatmap column headers**
Right after each call type column header name. So "Cold outreach (i) / baseline 12.7%" with the (i) being the tooltip trigger.

**3. View 2 filter pills**
Inside each pill, after the label and count: "Cold outreach (n=79, 53%) (i)" — the (i) icon is the tooltip trigger.

### Tooltip behavior

- Hover-triggered (not click)
- Tooltip box appears below or to the right of the (i) icon
- Soft shadow, white background, ~280px wide max
- Text content from `callTypeDefinitions`, slightly smaller than body text
- Disappears on mouseout
- Mobile fallback: tap-to-show, tap-elsewhere-to-dismiss (basic implementation, no fancy interaction)

### Visual style of the (i) icon

- Small (~14px diameter)
- Soft gray (`var(--text-soft)` or similar) on default
- Slightly darker on hover
- Uses Unicode `ⓘ` character or a simple CSS-styled circle with "i" inside — designer's call
- Cursor: help (CSS `cursor: help`)

## What NOT to change

- Underlying JS data structure keys (`inbound_followup`, `in_flight_followup`, `confirmation`)
- Filter logic, sort logic, calculations
- View names (View 1 / View 2 / View 3 stay)
- Confidence labels, color schemes, all other visual elements
- Anything in View 2's behavior table
- The (i) icons should NOT appear on rep names, behavior names, or anywhere else other than call type labels

## Output

Save updated file in place at `[PATH TO]/owner_dashboard.html`.

Print to stdout when done:
- "Fix 1 applied: call type display labels renamed (Inbound leads, Re-engagement, Demo confirmation)"
- "Fix 2 applied: (i) tooltip icons added next to call type labels in headline chart, heatmap headers, and View 2 filter pills"

If any rename can't be located or any tooltip can't be added cleanly, report which and stop.
