# Owner.com Sales Intelligence — Executive Summary

*Applied AI Lead case study · Alpha Wong · May 2026*

---

## Situation

Owner runs over a dozen outbound sales reps making 120+ dials per day — roughly 1,440 dials daily. Upstream, the AI stack is strong: concept fit classification, pickup prediction, lead routing, automated pre-call research. What happens *during* the call is not measured systematically. Coaching is anecdotal. Reps go in with restaurant facts but no call strategy. As volume grows, this gap compounds: every call without behavioral measurement is a lost learning signal, and best practices stay locked in the heads of individual top performers.

## What the data shows

Three findings from the 150-call sample shaped the build.

- **Pipeline stage drives a 6× spread in booking rates.** Cold outreach books at 13%; demo confirmation books at 78%. Cold outreach is also the largest single bucket — 53% of all dials. Volume × rate is where leverage compounds, and cold outreach is where the leverage lives.

- **Rep performance variance is mostly call-mix variance.** Raw rep booking rates spread from 0% to 100%. Once controlled for call type, most of that compresses. Some "top performers" are working higher-baseline queues; some "weak performers" are working harder ones at above-baseline rates. Coaching off raw rates would coach the wrong people.

- **Within call types, specific behaviors correlate with booking.** Reps who paraphrase prospects' words, propose specific times, and adapt the pitch to discovery answers book at substantially higher rates within cold outreach. Pattern is consistent at the prototype scale; would resolve into confirmed signal within weeks of continuous scoring at production volume.

## Why it matters

A meaningful lift on cold-outreach booking rate is the highest-leverage move available — same product, same reps, no change in lead targeting or dial volume. Beyond the booking rate, the org gains a compounding advantage: every new rep ramps faster because best practices are codified rather than tribal; the existing AI investment (concept fit, pickup prediction, PCR) gets activated downstream where deals are actually won or lost.

## What we built

Two products, one shared transcript-scoring pipeline.

A manager-facing diagnostic that surfaces what's working at scale across the call corpus, honest about confidence so managers know when to act and when to wait. And a rep-facing companion that brings that intelligence into the moment of the call, mapped to call phases, designed as an upgrade to the existing Salesloft PCR panel rather than a new tool reps have to learn.

Core logic: classify each call by type first, then derive a behavioral schema specific to that call type via qualitative analysis of its transcripts, then score continuously against the appropriate schema. Managers review and promote candidate behaviors to "best practice" status. Promoted patterns flow into the rep companion. Rep adherence becomes coachable. As call volume grows, the system gets sharper.

The current build includes a fully derived schema for cold outreach (the highest-volume, lowest-yielding call type, where leverage compounds most) and a preliminary schema for inbound leads. Re-engagement and demo confirmation schemas are scoped as deferred work.

## To move forward, we need

1. **Greenlight a structured pilot** — briefed reps vs. matched controls, 30-day measurement window. Booking rate is the leading indicator; show rate and close rate come into view once CRM funnel data is connected.
2. **Designate a sales operations owner** for the manager pattern-promotion workflow. Managers, not the AI, decide what becomes "best practice."
3. **Approve engineering coordination** for live data integration (Snowflake nightly job + Salesloft PCR panel upgrade).
