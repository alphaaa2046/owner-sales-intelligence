# Brief Build — Canonical Prompt

This is the final canonical prompt for `owner_brief.html`. It produces the deliverable in its current state: a single-file HTML mockup of the Rep Prep Companion that serves cold outreach restaurants with full pre-generated content and inbound-leads restaurants with a per-phase behavior preview pointing to where production content would come from.

The brief lives, in production, as an upgrade to Salesloft's existing PCR custom panel — not a standalone tool. The HTML mockup demonstrates the in-call experience.

---

## Output

Single file: `owner_brief.html` — self-contained HTML with embedded CSS and JS. No build step. Opens directly in browser.

## Visual approach

Small focused tool, max width ~640px, centered. Same accent color and font stack as the dashboard. Lean and demo-focused, not over-designed. Looks like something that lives inside a Salesloft side panel.

A small banner at the top: "Prototype mockup — in production, this lives as an upgrade to Salesloft's existing PCR panel rather than a standalone tool."

## Page structure

```
[Banner]
[Heading: Rep Prep Companion]
[Restaurant selector dropdown]
[Restaurant context panel]
[Four phase cards: Opening / Discovery / Pitch / Close]
[Feedback widget]
[Footer with About link]
```

## Restaurant data

10 demo restaurants. Six are cold outreach; four are inbound leads. Hardcode each restaurant's data including: id, name, cuisine, num_locations, city, third-party platforms, owner_name, lead source description, last interaction context, Google ranking string, fit_tier, call_type, and a `default_expanded_phase` indicating which card opens by default.

```js
const restaurants = [
  // Cold outreach restaurants
  {
    id: "rest_001",
    name: "Buffalo Joe's Wings",
    cuisine: "American (Wings)",
    locations: 2,
    city: "Hillsborough, NC",
    third_party: ["DoorDash", "Uber Eats"],
    owner_name: "Mike Henderson",
    lead_source: "cold outreach",
    last_interaction: "no prior contact",
    google_position: "#4 for 'best wings Hillsborough'",
    fit_tier: "high",
    call_type: "cold_outreach",
    default_expanded_phase: "pitch"
  },
  // 5 more cold outreach restaurants (rest_002, rest_004, rest_006, rest_007, rest_009)
  // 4 inbound followup restaurants (rest_003, rest_005, rest_008, rest_010)
];
```

For inbound restaurants, `last_interaction` references their inbound action ("form fill 3 days ago", "request submitted", "referral from rest_011", etc.). `lead_source` is "inbound followup" or "inbound — form fill (N days ago)" style.

## Restaurant selector

A dropdown at the top. Default = rest_001 (Buffalo Joe's, cold outreach). Selecting a different restaurant re-renders all panels below.

## Restaurant context panel

Two-column compact layout showing the restaurant's facts:

```
Buffalo Joe's Wings · 2 locations · Hillsborough, NC
American (Wings) · Owner: Mike Henderson

Lead source:        Cold outreach (no prior contact)
Third-party:        DoorDash, Uber Eats
Google ranking:     #4 for "best wings Hillsborough"
Fit tier:           High
```

Italic note below: *In production, all fields auto-populate from PCR. Some values shown here are illustrative for demo purposes — Google ranking and fit tier come from existing Owner systems.*

## Four phase cards: behavior diverges by call type

Below the restaurant context, four cards in order: Opening / Discovery / Pitch / Close. Each card has a header bar that's clickable to expand/collapse. Visual: clear chevron or arrow indicator; subtle background tint when collapsed; full content visible when expanded.

**Default expansion logic:** for each restaurant, hardcode which card is expanded by default in `default_expanded_phase` field. Accordion behavior — clicking a different card collapses the currently expanded one. Suggested defaults:

| Restaurant | Call type | Default expanded |
|---|---|---|
| Buffalo Joe's Wings | cold_outreach | pitch |
| El Sabor Mexicano | cold_outreach | pitch |
| Saigon Bowl | cold_outreach | pitch |
| Akita Sushi | cold_outreach | pitch |
| The Burger Joint | cold_outreach | pitch |
| Mediterranean Grill | cold_outreach | pitch |
| Nonna's Pizza | inbound_followup | discovery |
| Sunny Side Cafe | inbound_followup | discovery |
| Mama's Soul Kitchen | inbound_followup | close |
| Spice Garden | inbound_followup | discovery |

### Cold outreach restaurants — full pre-generated card content

For cold outreach restaurants (`call_type === "cold_outreach"`), each card shows full content:

**Opening card** (when expanded): one verbatim suggested opener + small footnote with linked behavior

```
Suggested opener:

> "Hi Mike, this is [rep name] from Owner. I was looking at Buffalo Joe's online —
> you're showing up #4 when I search for best wings in Hillsborough, behind a
> couple of places that don't have nearly your review counts. Quick question —
> got a couple minutes?"

⓵ Linked: research_hook_used = specific_findings · Differentiator (+28pts)
```

**Discovery card** (when expanded): one primary verbatim question + brief rationale + small footnote, with collapsible "Alternate questions" expander showing 2 more.

**Pitch card** (when expanded): the most likely friction for this restaurant + verbatim handler + small footnote with linked behaviors, plus a collapsible "Other likely frictions" expander showing 2-3 alternate frictions with shorter handlers.

**Close card** (when expanded): one specific time proposal verbatim + small footnote, with collapsible alternate close framing.

For each cold restaurant, hardcode the full content per card. The behavior linkages reference the dashboard's cold-outreach Differentiators.

### Inbound restaurants — schema-preview cards with production note

For inbound restaurants (`call_type === "inbound_followup"`), each card shows a behavior list scoped to the inbound schema preview, NOT a verbatim handler. When expanded:

**Opening card content:**
```
Behaviors that matter in inbound openings:

  • inbound_action_referenced_specifically — opening with the prospect's
    exact action (form fill, request, referral)
  • stale_lead_handling — if the lead is old, acknowledging and reframing
    rather than treating it as fresh

In production, this card surfaces a verbatim handler for the most relevant
behavior on this call. The current prototype's verbatim content covers
cold outreach only — see Buffalo Joe's Wings for an example.
```

**Discovery card content:**
```
Behaviors that matter in inbound discovery:

  • motivation_question_asked — asking what prompted the prospect's interest
  • volume_qualification_done — qualifying fit by volume / order source
    before pitching
  • rapport_moment_created — building on context the prospect provides

In production, this card surfaces a verbatim handler for the most relevant
behavior on this call. The current prototype's verbatim content covers
cold outreach only — see Buffalo Joe's Wings for an example.
```

**Pitch card content:**
```
Behaviors that matter in inbound pitch:

  • specialist_handoff_framing — positioning as a scheduler ("I'm just
    the person who schedules meetings") rather than re-pitching the full
    product
  • timing_objection_response — handling "I'm busy" / "not for 6 months"
    with a fast, credible counter
  • pricing_handling — proactive transparency or specialist deferral
    (vs. vague deflection)

In production, this card surfaces a verbatim handler for the most relevant
behavior on this call. The current prototype's verbatim content covers
cold outreach only — see Buffalo Joe's Wings for an example.
```

**Close card content:**
```
Behaviors that matter in inbound close:

  • partner_inclusion_handled — when prospect says "need to check with my
    partner," offering to include them rather than accepting the delay
  • specific_time_proposed — proposing a specific day/time, not open-ended
    "when works for you"

In production, this card surfaces a verbatim handler for the most relevant
behavior on this call. The current prototype's verbatim content covers
cold outreach only — see Buffalo Joe's Wings for an example.
```

The same per-phase content displays for all four inbound restaurants — it's keyed on call_type, not restaurant.

### Visual treatment for inbound expanded cards

- Behavior list rendered with bullet points (subtle small bullets, not heavy)
- Behavior name in monospace or styled (matching how field names render in the dashboard's behavior table)
- Em-dash separator between behavior name and short description
- Production note below the bullet list, in italic, slightly muted color
- No verbatim handler boxes, no linked-behavior tags
- Empty space should feel intentional, not broken — the production note explains why

## Feedback widget

Below all four phase cards, a single feedback section for the whole brief:

```
Was this brief helpful for this call?  [👍 helpful]  [👎 not helpful]

[optional: leave a comment...]
```

Click toggles to "selected" state, stores in browser memory only. After click, show: "Thanks — feedback like this refines the brief over time. In production, ratings flow into the dashboard's signal."

Same banner: "Stored in-memory for this prototype. Not persisted."

## Footer

```
Prototype mockup · 10 demo restaurants · About
```

About link opens a small modal:

```
About this prototype

This is a static mockup of the Rep Prep Companion. In production:

- Restaurant data auto-populates from PCR (Salesloft side panel)
- Suggested opener and scenario responses generate dynamically based on
  patterns from continuous call scoring
- This functionality lives inside PCR rather than as a standalone tool
- Rep feedback (👍/👎) flows back into prompt refinement and dashboard signal

The 10 restaurants here are illustrative. Production runs across the full
call queue with content tuned per call type, segment, and individual rep.
The behavioral framework underlying card content is derived per call type
from qualitative analysis of that call type's transcripts. The current
prototype includes a full cold-outreach schema (used by cold restaurants)
and a preliminary inbound schema (visible in inbound restaurant cards
without verbatim handlers).
```

## What NOT to build

- No live API calls — everything hardcoded
- No actual audio/voice integration
- No login or auth
- No persistent storage (feedback is in-memory only)
- No mobile-specific responsive behavior beyond reasonable defaults
- No animations or transitions beyond simple panel show/hide
- No charting or data viz — this is a content-display tool, not analytical
- No links between this and the dashboard file — they're separate files
- No "ON THE BEHAVIOR FRAMEWORK" callout panel between cards and feedback (provenance framing lives in the dashboard's methodology note and supporting docs)

## Layout / styling

- Same accent color and font stack as the dashboard for visual consistency
- Single column, max width ~640px, centered
- Comfortable spacing — looked at mid-call, scannable matters
- Section headers in slightly larger weight, panels separated by visible spacing
- Suggested opener and verbatim pattern blocks rendered in a slightly different background tint to make them stand out as "what to say"
- Buttons: large, clear, easy to tap

Don't overdesign. Plain, functional, demo-friendly.

## Output

Save file at `[PATH TO]/owner_brief.html`.

Print to stdout when done:
- "Brief mockup built at: owner_brief.html"
- "10 restaurants: 6 cold outreach (full content) + 4 inbound followup (schema preview)"
- "One card expanded by default per restaurant; others collapsible"
- "Single feedback section at bottom (in-memory only)"
