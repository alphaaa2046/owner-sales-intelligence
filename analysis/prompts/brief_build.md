# Claude Code Prompt: Owner Brief — Rebuild

REBUILD the existing `owner_brief.html` from scratch with a new structure. Existing file at `[PATH TO]/owner_brief.html` will be replaced.

The previous version was overdesigned — it explained the rationale behind each scenario (WHAT THEY'RE LIKELY DOING / WHAT'S WORKED / WHY THIS WORKS). That's a teaching artifact, not an in-call tool. A rep mid-call needs to scan in 3 seconds and find the thing to say. This rebuild is for that use.

## Output

Save to `[PATH TO]/owner_brief.html` (replacing existing). Same single-file, no-build, browser-friendly approach as before.

## Visual approach

Same as previous brief — small focused tool, max width ~640px, centered, lean and demo-focused. Same accent color and font stack as the dashboard. Don't overdesign. The brief should look like something that lives inside a Salesloft side panel.

## Top-of-page elements

1. Banner at top: "Prototype mockup -- in production, this lives as an upgrade to Salesloft's existing PCR panel rather than a standalone tool."
2. Restaurant selector dropdown (10 restaurants, default = rest_001 Buffalo Joe's Wings)
3. Restaurant context panel — keep similar to previous version, but tighter

### Restaurant context panel (compact)

Two-column compact layout:

```
Buffalo Joe's Wings · 2 locations · Hillsborough, NC
American (Wings) · Owner: Mike Henderson

Lead source:        Cold outreach (no prior contact)
Third-party:        DoorDash, Uber Eats
Google ranking:     #4 for "best wings Hillsborough"
Fit tier:           High
```

Small italic line below: *In production, all fields auto-populate from PCR. Some values shown here are illustrative for demo purposes — Google ranking and fit tier come from existing Owner systems.*

## Four call-phase cards

Below the restaurant context, four cards in this order: **Opening · Discovery · Pitch · Close.**

Each card has a header bar that's clickable to expand/collapse. Visual: clear chevron or arrow indicator; subtle background tint when collapsed; full content visible when expanded.

**Default expansion logic (per restaurant):**
For each restaurant, hardcode which card is expanded by default. The expanded card = the call phase where this restaurant has the most likely friction or highest-leverage moment based on its data.

For Buffalo Joe's Wings (`rest_001`): **Pitch** is expanded by default (third-party + Google visibility friction is high). Opening/Discovery/Close are collapsed.

Per restaurant, hardcode `default_expanded_phase` field: one of `"opening" | "discovery" | "pitch" | "close"`.

The user can click any card to expand/collapse — only one card expanded at a time (accordion behavior). When user clicks a different card, current expanded card collapses.

## Card content — keep it ruthlessly scannable

Each card has minimal content. No interpretation paragraphs. One concrete thing per card.

### Opening card content

ONE suggested opener (verbatim line, ready to use). Small footer tag.

For Buffalo Joe's:

```
[OPENING — collapsed by default]

Suggested opener (verbatim, reference Mike's name and the Google finding):

> "Hi Mike, this is [rep name] from Owner. I was looking at Buffalo Joe's
> online — you're showing up #4 when I search for best wings in Hillsborough,
> behind a couple of places that don't have nearly your review counts. Quick
> question — got a couple minutes?"

⓵ From cold-outreach booked-call patterns. Linked: research_hook_used = specific_findings · Differentiator (+28pts)
```

The blockquote is the verbatim line. The footer tag is small italic and refers to the dashboard.

For OTHER restaurants, generate a parallel opener using the restaurant data (owner name, restaurant name, the specific Google finding for cold outreach; or the form-fill acknowledgment for inbound). Hardcode `suggested_opener` per restaurant.

### Discovery card content

ONE primary question (verbatim, expanded). Two ALTERNATE questions, collapsed.

For Buffalo Joe's (cold outreach):

```
[DISCOVERY — collapsed by default]

Primary question:

> "Where are most of your orders coming from right now? Walk-ins, third-party
> apps, or are you running your own online ordering?"

Why this question first: it surfaces the third-party dependence quickly,
which sets up the rest of the conversation.

⓵ Linked: discovery_question_asked = before_pitch · +13.9pts · Possible differentiator

[Alternate questions ▾]   <-- collapsible expander

  Alternate 1:
  > "Do you spend anything on marketing right now? Even a little? What's
  > working?"

  Alternate 2:
  > "How busy is your kitchen right now during peak? Are you turning orders
  > away?"
```

The "Alternate questions ▾" is a small collapsible widget WITHIN the Discovery card. Default collapsed. Click to reveal the two alternate questions. Each alternate is a one-line verbatim, no rationale.

For OTHER restaurants, hardcode primary + 2 alternates. For inbound leads especially, the primary question should reference the form fill acknowledgment style.

### Pitch card content (the most complex card)

ONE primary friction handler (expanded), TWO alternate friction handlers (collapsed).

For Buffalo Joe's (cold outreach, on DoorDash + Uber Eats), primary friction = third-party objection.

```
[PITCH — EXPANDED BY DEFAULT for Buffalo Joe's]

Most likely friction: third-party platform objection.

Verbatim handling line (specific dollar math + reframe):

> "You're probably paying around $1,200-1,500 a month in commissions to
> DoorDash on your volume. Owner is $349 a month flat — and you keep
> ownership of the customer. Want me to walk through the actual math on your
> numbers?"

⓵ Linked: third_party_handling = proactive_reframe · +23.6pts · Differentiator
   Linked: commission_math_specific = specific_dollars · +18.6pts · Possible differentiator

[Other likely frictions ▾]   <-- collapsible expander, default collapsed

  Friction: "We tried something like this before."
  > "Got it — that happens a lot. What specifically didn't work? Was it the
  > tech, or volume not picking up?"
  ⓵ tried_before_objection_handled · candidate

  Friction: POS/integration question (e.g., "How does this work with Toast?")
  > "Toast integration is solid — orders, menu, customer data all sync.
  > Quick question first: are you using Toast for just POS, or also online
  > ordering today?"
  ⓵ rep_used_prospect_answer = explicit · +27.1pts · Differentiator
```

For OTHER restaurants, hardcode the primary friction based on their data:
- Restaurants on multiple third-party platforms → primary friction = third-party
- Restaurants with prior interaction → primary friction = "tried before"
- High-fit single-location restaurants → primary friction = POS/integration question

Each restaurant gets:
- `pitch_primary_friction`: the primary friction with verbatim handler
- `pitch_alternate_frictions`: array of 1-2 alternate frictions with verbatim handlers (could be empty if data doesn't suggest alternates)

### Close card content

ONE specific time proposal (verbatim). Possibly one alternate framing.

For Buffalo Joe's:

```
[CLOSE — collapsed by default]

Suggested close:

> "Tuesday at 2pm or Wednesday at 10am — which works better? I'll send a
> calendar invite and we'll dig into your numbers specifically. Not trying
> to make you decide right now, just want to show you what we do."

⓵ Linked: specific_time_proposed = specific · +32.6pts · Differentiator

[Alternate close ▾]

  Lower-pressure framing:
  > "Want me to send some info to your email and follow up next week, or
  > would 15 minutes on Tuesday work better?"
```

Same alternate-collapsible pattern as Discovery.

## Restaurant data structure

Same 10 restaurants as the previous prompt. Update each to include:

```js
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
  
  default_expanded_phase: "pitch",  // which card opens by default
  
  // Card content per phase
  opening: {
    suggested_opener: "Hi Mike, this is [rep name] from Owner. I was looking at Buffalo Joe's online — you're showing up #4 when I search for best wings in Hillsborough, behind a couple of places that don't have nearly your review counts. Quick question — got a couple minutes?",
    linked_behaviors: ["research_hook_used = specific_findings · Differentiator (+28pts)"]
  },
  discovery: {
    primary_question: "Where are most of your orders coming from right now? Walk-ins, third-party apps, or are you running your own online ordering?",
    primary_rationale: "Surfaces the third-party dependence quickly, which sets up the rest of the conversation.",
    primary_linked: "discovery_question_asked = before_pitch · +13.9pts · Possible differentiator",
    alternates: [
      {q: "Do you spend anything on marketing right now? Even a little? What's working?"},
      {q: "How busy is your kitchen right now during peak? Are you turning orders away?"}
    ]
  },
  pitch: {
    primary_friction: "Third-party platform objection (DoorDash/Uber Eats commissions).",
    primary_handler: "You're probably paying around $1,200-1,500 a month in commissions to DoorDash on your volume. Owner is $349 a month flat — and you keep ownership of the customer. Want me to walk through the actual math on your numbers?",
    primary_linked: ["third_party_handling = proactive_reframe · +23.6pts · Differentiator", "commission_math_specific = specific_dollars · +18.6pts · Possible differentiator"],
    alternates: [
      {
        friction: "\"We tried something like this before.\"",
        handler: "Got it — that happens a lot. What specifically didn't work? Was it the tech, or volume not picking up?",
        linked: "tried_before_objection_handled · candidate"
      },
      {
        friction: "POS/integration question (e.g., \"How does this work with Toast?\")",
        handler: "Toast integration is solid — orders, menu, customer data all sync. Quick question first: are you using Toast for just POS, or also online ordering today?",
        linked: "rep_used_prospect_answer = explicit · +27.1pts · Differentiator"
      }
    ]
  },
  close: {
    primary_close: "Tuesday at 2pm or Wednesday at 10am — which works better? I'll send a calendar invite and we'll dig into your numbers specifically. Not trying to make you decide right now, just want to show you what we do.",
    primary_linked: "specific_time_proposed = specific · +32.6pts · Differentiator",
    alternates: [
      {
        framing: "Lower-pressure framing",
        text: "Want me to send some info to your email and follow up next week, or would 15 minutes on Tuesday work better?"
      }
    ]
  }
}
```

For the other 9 restaurants, populate similarly. Each gets full content for all four cards (don't truncate cards on non-hero restaurants — every card is concise enough that filling all four for all 10 restaurants is reasonable). Vary which card is `default_expanded_phase` based on the restaurant's likely friction:

| Restaurant | default_expanded_phase | Why |
|---|---|---|
| rest_001 Buffalo Joe's | pitch | DoorDash + Uber Eats |
| rest_002 El Sabor | pitch | DoorDash + cold outreach |
| rest_003 Nonna's Pizza | discovery | Inbound lead, slow down to qualify |
| rest_004 Saigon Bowl | pitch | Multi-platform third-party |
| rest_005 Sunny Side | discovery | Inbound, multi-location complexity |
| rest_006 Akita Sushi | pitch | Single platform but third-party |
| rest_007 Burger Joint | pitch | All three platforms — high friction |
| rest_008 Mama's Soul | close | Inbound + referral, ready to close |
| rest_009 Mediterranean | pitch | Cold + GrubHub |
| rest_010 Spice Garden | discovery | Inbound + multi-platform complexity |

For each restaurant, the four cards' content should be tailored. Use the patterns from Buffalo Joe's as templates — same structure, restaurant-appropriate content. Generate plausible content using each restaurant's data (city, owner, third-party platforms, fit tier).

For inbound leads, the Opening should reference the form fill or referral, not a Google research hook. The Discovery primary question should be a soft "what brought you to Owner" or similar.

## Single feedback section at the bottom of the brief

Below all four cards, ONE feedback section for the whole brief:

```
Was this brief helpful for this call?  [👍 helpful]  [👎 not helpful]

[optional: leave a comment...]
```

Click toggles to "selected" state, stores in browser memory only. After click, show: "Thanks — feedback like this refines the brief over time. In production, ratings flow into the dashboard's signal."

Same banner: "Stored in-memory for this prototype. Not persisted."

## Footer

Same as previous: "Prototype mockup · 10 demo restaurants · About"

About modal content stays similar to previous version.

## What NOT to build

- Don't reproduce the verbose "WHAT THEY'RE LIKELY DOING / WHAT'S WORKED / WHY THIS WORKS" structure from the previous version
- Don't add new features beyond what's specified
- Don't make cards visually heavy — small text, generous white space, clean
- Don't add chartjs or any visualization libraries
- Don't add multiple feedback widgets per card — single feedback at the bottom

## Layout / styling notes

- Cards: rounded corners, subtle border, expandable header with chevron arrow
- Verbatim quoted lines: rendered in slight background tint with left border accent (visual cue for "what to say")
- Small footer tags (`⓵ Linked: ...`) in muted text, italic, smaller font
- Sub-collapsibles within cards (Alternates, Other frictions): subtle inline expander with `▾` arrow, light background
- Whole brief is scannable in 5-10 seconds for the expanded card; the rep should be able to read the verbatim line in 2 seconds and say it

## Output

Save file at `[PATH TO]/owner_brief.html`. Replaces existing.

Print to stdout when done:
- "Brief mockup rebuilt at: owner_brief.html"
- "Four cards per restaurant: Opening / Discovery / Pitch / Close"
- "One card expanded by default per restaurant; others collapsible"
- "Pitch and Discovery cards have nested alternates that are collapsible"
- "Single feedback section at bottom (in-memory only)"

If anything's unclear, stop and ask.
