# Behavioral Scoring Prompt

This is the system prompt used by `analysis/scripts/score_transcripts.py` to score each call transcript against a 23-field behavioral schema.

The schema captures rep-controlled behaviors organized into 5 phases (Opening, Discovery, Value Proposition, Close, Wrap). Each field is either a categorical value (e.g., `specific | open_ended | not_reached`) or a boolean.

Note: this is the v2 schema. An earlier v1 used 12 fields with mostly binary scoring. v2 expanded the schema after analysis showed binary scoring lost meaningful execution-quality signal — for example, "research hook used: yes/no" doesn't distinguish a generic "I was looking around at restaurants in the area" from a specific "you're showing up #6 for best mexican near me." The v2 categorical values capture that distinction.

---

## System prompt

```
You are scoring an Owner.com sales call transcript on 23 rep-controlled behavioral elements organized into 5 phases.

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
```

## User message format

For each call, the user message passed to the API:

```
Score this complete transcript (outcome: <call_outcome>, call_type: <call_type>, duration: <duration> min):

<transcript>
```

The model is given the call_outcome and call_type as context (these are not target labels — they're metadata that helps the model interpret what kind of call it's looking at).
