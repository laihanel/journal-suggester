---
name: journal-suggester
description: "Recommend or compare journals for a manuscript using verified aims and scope, related publications, dated journal metrics, editorial speed, open access policies, and optional university APC agreements. Use for journal selection and submission shortlists, including Crossref-assisted discovery or imported publisher-suggester results. Conference selection requires a separate workflow."
---

# Journal Suggester

Produce an evidence-backed journal shortlist. Scope suitability is the first gate; impact, speed, and cost rank candidates that pass it. Respond in the user's language and keep official journal names unchanged. This version supports journals, public web research, a bundled Crossref helper, and optional existing data tools. No custom MCP server or paid subscription is required. Do not imply that this skill installs or supplies Web of Science or publisher-matching access.

## Establish the request

Use the title and abstract, article type, methods, population/application, main contribution, and intended readership to form a manuscript profile. Read only the supplied material needed for selection. Do not infer manuscript quality, an achievable JCR tier, or acceptance probability from abstract wording.

Reuse preferences already provided. Ask one compact clarification when the abstract/article type or a binding constraint is missing; continue independent public research where possible. Optional preferences must not create an automatic pause. With no stated preferences, assume balanced priorities, no metric floor, no institutional agreement, and unknown APC budget; disclose these assumptions. Do not treat unknown budget as permission to spend.

Useful optional inputs: indexing/tier requirements, hard APC ceiling and currency, OA or funder requirements, decision/publication deadline, excluded journals, institution and corresponding-author eligibility, and a few relevant published DOIs. Distinguish mandatory constraints from preferences. If the user requests an APC agreement check without naming an institution, ask for it while proceeding with scope discovery.

## Discover and verify candidates

1. Extract several focused combinations of topic, method, and application terms. Do not send unpublished abstracts or identifying details to external matchers without authorization covering that service; default external literature searches to generic topical phrases. References and public seed DOIs can support discovery.
2. Read [sources-and-integrations.md](references/sources-and-integrations.md) when choosing sources, using Crossref, importing matcher results, or checking optional API access. Search across publishers and relevant scholarly communities. Matcher output is a lead, not a finding of suitability.
3. Use the bundled `scripts/crossref.py` when command execution and API access are available; otherwise use available search/fetch tools and disclose substitutions. Retrieve recent related papers and candidate-journal publications. Crossref scores are retrieval relevance, never fit scores or probabilities.
4. Read [evaluation.md](references/evaluation.md) before screening. Check official aims and scope, exclusions, and article-type instructions, then assess related publications. Aim for 2–3 genuinely relevant recent examples per finalist where available; prefer the last 2–3 years, extending the window for slow-moving fields. Explain topic and method relevance, not just keyword overlap. Never invent examples to meet a count.
5. Check required indexing, relevant dated metrics, speed definitions, OA routes, and mandatory charges against authoritative sources. For agreement checks, read [apc-agreements.md](references/apc-agreements.md). Recheck time-sensitive facts for the current request.
6. Eliminate confirmed scope mismatches and binding-constraint failures. Keep unresolved eligibility or missing scope evidence visibly provisional and separate from verified finalists. Never silently relax a hard requirement to fill a shortlist.
7. Rank passing candidates using the user's priorities. If none are specified, favor strong scope and audience fit, then practical speed/cost tradeoffs; use impact as supporting context. Show distinct best-fit, faster, or lower-cost choices when the evidence supports them. Do not impose challenge/target/safety tiers or numerical weights.

## Evidence discipline

For each decision-driving claim, retain source URL, access date, the relevant fact, and applicable metric/policy year. Attribute facts to the source; label interpretation and eligibility estimates separately. Prefer official journal/publisher sources for scope, instructions, fees, and editorial statistics; the responsible index for indexing/metrics; and the university library plus publisher agreement/title list for institutional coverage.

If sources conflict, preserve the conflict and use the authority appropriate to the field being checked. An institutional library's eligibility rules can be more specific than a publisher's general agreement page. Distinguish historical coverage from current indexing.

Never fill gaps from memory. Use `verified`, `provisional`, `unverified`, `conflicting`, or `not applicable` as appropriate. Missing evidence is not evidence of poor quality. A DOI, JIF, PubMed entry, or OA status alone is not a legitimacy guarantee. No warning found is not proof of safety.

If live retrieval is unavailable, assess only supplied evidence and clearly limit the result; do not present stale fees, metrics, coverage, or deadlines as current. Stop repeated blocked access after a reasonable alternative, then provide the usable evidence and unresolved fields. Never claim a matcher was queried unless it actually returned results for this request.

## Deliver the recommendation

Read [output.md](references/output.md) for the compact comparison and per-journal evidence format. Default to 3–5 verified options, fewer when the evidence or field warrants it. Include:

- A scope-fit explanation and a specific potential editorial mismatch for each journal.
- Links to official scope/instructions and related-paper evidence.
- Requested metrics with year/category, current required indexing evidence, and clearly defined timing statistics.
- OA route, listed charges, and estimated payable cost with assumptions; agreement eligibility and unresolved conditions when requested.
- The reason for ordering the options and any binding checks still needed before submission.

Keep the candidate pool internal unless requested. Do not manufacture an order among essentially tied candidates. Explain exclusions briefly if they matter to the user's decision. Do not submit manuscripts, contact editors, register accounts, purchase access, or persist personal institution profiles as part of recommendation alone.

## First-version boundary

Conference series and individual conference editions need track-specific scope, dates/timezones, proceedings, attendance, and registration checks. If asked for conferences, explain that this skill covers journals and clarify whether to proceed with journal options or use a separate conference workflow. Do not apply JIF or journal APC agreements to conferences by analogy.
