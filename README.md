# Journal Suggester

An agent skill for finding journals that fit a manuscript, then comparing publication speed, journal metrics, open access options, and author costs.

The skill checks **aims and scope first**. A high impact factor, low fee, or publisher match score cannot override a confirmed scope mismatch. Recommendations link to supporting evidence and identify facts that remain unverified.

## What it does

- Matches the research topic, methods, article type, contribution, and intended audience to journal scope and submission requirements.
- Looks for related publications across publishers, with a bundled Crossref helper for public metadata retrieval.
- Compares available JIF/JCR information and other metrics with their years, categories, and sources.
- Separates first editorial decision, post-review decision, acceptance, and online-publication timing.
- Compares OA routes, listed APCs, other mandatory charges, and estimated author-payable costs.
- Optionally checks university APC agreements against the institution, corresponding author, journal, article type, and agreement dates.
- Uses available publisher-suggester results or user-provided exports as discovery leads, followed by independent verification. See the [Journal Selection Tools directory](#journal-selection-tools) for provider links and inputs.

Version 1 covers **journals**. Conference recommendations need a separate workflow.

## Requirements

- Codex with skill support. Other agents that support `SKILL.md` may be able to use the instructions, but have not been tested with this package.
- Web search or page-reading tools for current scope, fees, metrics, and policies. Without live access, the skill can assess supplied evidence with explicit limitations.
- Python 3.9 or newer and outbound HTTPS access to `api.crossref.org` to use the optional Crossref helper. It uses only Python's standard library.

No custom MCP server, paid database subscription, or API key is required for the basic workflow. The helper does not call the OpenAI API or require an `OPENAI_API_KEY`. Your agent environment may have its own account or usage requirements.

## Install in Codex

Download or clone this repository. Install the **entire `journal-suggester` folder**, including its references, scripts, and agent metadata.

For a user-level installation on macOS or Linux, run these commands from the downloaded repository root:

```bash
mkdir -p "$HOME/.agents/skills"
cp -R journal-suggester "$HOME/.agents/skills/"
```

For a project-level installation, copy the folder into your target project's `.agents/skills/` directory instead. The resulting entry point should be:

```text
your-project/.agents/skills/journal-suggester/SKILL.md
```

For either installation, if a `journal-suggester` folder already exists at the destination, review and replace that installation deliberately rather than nesting another copy inside it. Keep one active copy to avoid ambiguous versions. Start a new Codex session after installation.

The user- and project-level directories follow the [official OpenAI installation guidance](https://developers.openai.com/api/reference/cli). See also the [official skill documentation](https://learn.chatgpt.com/docs/build-skills). Installation details can vary as agent environments evolve.

## Use the skill

Invoke it explicitly with `$journal-suggester`, then provide your abstract and any important constraints. An installed skill can also be selected automatically when a request matches its description.

### Basic recommendation

```text
Use $journal-suggester to recommend 3–5 journals for this manuscript.
Prioritize aims and scope, then balance speed, visibility, and cost.

Article type: Original research
Title: [your title]
Abstract: [your abstract]
```

If no preferences are supplied, the skill assumes balanced priorities, no metric floor, unknown APC budget, and no institutional agreement. It does not estimate acceptance probability or assign a journal tier from abstract wording.

### Apply cost, indexing, and timing preferences

```text
Use $journal-suggester for the abstract below.

Required indexing: SCIE; verify the collection rather than inferring it from JIF.
Hard total author-payable budget: USD 1,000, including mandatory charges.
OA: Optional; include subscription routes.
Timing preference: A first decision after external review within 90 days.
Treat this as a preference, not a guarantee.

Article type: Original research
Abstract: [your abstract]
```

### Check a university APC agreement

```text
Use $journal-suggester and check institutional APC coverage.

Institution and campus: [official name and country]
Corresponding author: Affiliated with this institution
Article type: Original research
OA requirement: CC BY
Expected submission period: [month/year]
Abstract: [your abstract]

Distinguish apparently eligible coverage from article-specific approval.
Identify journal exclusions, operative dates, caps, and remaining charges.
```

An institutional agreement does not automatically mean a zero-cost article. Final eligibility may depend on approval, acceptance date, and remaining funding.

### Compare known journals or imported suggestions

```text
Use $journal-suggester to compare [Journal A], [Journal B], and [Journal C]
for the abstract below. Prioritize scope and method fit.

I have attached a publisher-suggester CSV. Treat its scores as discovery
leads and independently verify the journal scopes and publication policies.

Abstract: [your abstract]
```

## What to expect

The default result is a shortlist of 3–5 supported options, or fewer when the evidence does not justify more. Each recommendation should include:

1. Why the journal fits, plus any specific editorial mismatch or requirement.
2. Official scope/instructions links and relevant published-paper examples.
3. Available dated metrics and indexing evidence, with source qualifications.
4. Clearly defined editorial/publication timing statistics.
5. OA routes, listed charges, estimated payable costs, and optional agreement eligibility.
6. A submission-priority rationale and unresolved checks.

Unavailable or conflicting information stays visible. Historical timing is not a promise of a decision or acceptance by a deadline. A shortlist is a submission aid, not an editorial decision.

## Crossref helper

The helper retrieves metadata; the agent performs the suitability assessment. Run these examples from the repository root:

```bash
# Find potentially related journal articles using public topic keywords.
python3 journal-suggester/scripts/crossref.py search \
  --query 'quadrotor recurrent neural residual control' \
  --from-date 2023-01-01 \
  --rows 10

# Retrieve recent journal-article records by ISSN.
python3 journal-suggester/scripts/crossref.py journal \
  --issn 1476-4687 \
  --from-date 2025-01-01 \
  --rows 10

# Resolve a published DOI.
python3 journal-suggester/scripts/crossref.py doi \
  --doi 10.1038/nphys1170
```

Dates illustrate publication windows; choose a suitable window for your request. `search` and `journal` also accept `--until-date`. All three commands accept `--timeout` and an optional `--mailto` address that you authorize sending to Crossref. See each subcommand's `--help` for details.

Successful requests emit JSON containing the request URL, retrieval time, records, and limitations. Retrieval failures emit JSON errors with a nonzero exit status; invalid command arguments produce standard command-line usage errors. The helper creates no persistent cache or output files unless you redirect its output yourself.

Crossref metadata and abstract coverage vary. Search scores are not journal-fit scores, records may be misclassified by depositors, and a DOI does not establish venue quality or current indexing. The helper does not supply JIF, official scope, current APCs, or institutional eligibility. See the [integration reference](journal-suggester/references/sources-and-integrations.md).

## Optional integrations

| Source | Role | Included in this repository? |
| --- | --- | --- |
| Crossref | Publication discovery and identifier resolution | Yes: Python helper |
| Web of Science Starter/Expanded | Additional literature and citation evidence | Guidance only; requires available authorized access |
| Web of Science Journals API | JCR journal metrics | Guidance only; separate paid licensing applies |
| JANE | PubMed-oriented journal discovery | Guidance only; no bundled adapter |
| Publisher journal finders | Additional candidate journals | Use available permitted browser access or imported results; no bundled matching adapters |

MCP is optional. A connector can expose an authorized source to the agent, but it does not supply subscriptions, bypass access controls, or make provider match scores interchangeable. Publisher/API capabilities should be checked when integrating them.

## Journal Selection Tools

Use these services to discover additional candidate journals. Publisher tools generally search their own portfolios; JANE and Web of Science use different scholarly collections. Combine suitable sources, then check each journal's official scope and recent publications independently.

Provider documentation was used to check the descriptions below. Links and documentation were reviewed on **November 17, 2026**; input fields, access requirements, metrics, and export features can change. Listing a service does not mean its interactive matching workflow has been tested or integrated into this skill.

| Tool | Coverage | What to enter | What it helps you inspect |
| --- | --- | --- | --- |
| [JANE: Journal/Author Name Estimator](https://jane.biosemantics.org/) | PubMed literature; useful for biomedical and life-science topics | Title, abstract, or topical keywords | Similarity-ranked journals and related articles; the [FAQ](https://jane.biosemantics.org/faq.php) describes its confidence scores, MEDLINE/DOAJ labels, and API. |
| [Web of Science Manuscript Matcher](https://mjl.clarivate.com/home?mm=) | Web of Science Core Collection | Manuscript title and abstract | Journal matches across publishers. Access may require sign-in; matching access and licensed JCR/API access are separate. |
| [Wiley Journal Finder](https://www.wiley.com/en-us/journal-finder) | Wiley journal portfolio | Title and abstract for matching, or subjects/topics for browsing | Relevant journals, metrics, publishing policies, and editorial timing; see [Wiley's comparison guide](https://www.wiley.com/publishing/article/authors/author-resources/how-to-choose-a-journal-for-publication). |
| [Elsevier JournalFinder](https://journalfinder.elsevier.com/) | Elsevier journal portfolio | Abstract, or keywords and other manuscript details | Candidate journals and available impact, publishing-time, and OA information. Confirm every selected journal's current policies and fees. |
| [Springer Nature Journal Finder](https://link.springer.com/journals) | Springer Nature portfolio, including Springer, Nature Portfolio, and BMC titles | Title, abstract, or keywords | Matching journals and available metrics, including median first-decision time. [Provider documentation](https://support.springernature.com/en/support/solutions/articles/6000134500-find-the-right-journal-for-your-manuscript) describes shareable results and CSV export. |
| [Taylor & Francis Journal Suggester](https://authorservices.taylorandfrancis.com/publishing-your-research/choosing-a-journal/journal-suggester/) | Taylor & Francis journal portfolio | Abstract or relevant keywords | Journal descriptions and available citation and publication-speed metrics. |
| [Sage Journal Recommender](https://journal-recommender.sagepub.com/) | Sage journal portfolio | Title and keywords | Matches with subject, indexing, and journal-type filters; see the [provider FAQ](https://journals.sagepub.com/page/journal-recommender-faqs). Sage Path is a separate transfer/submission service. |
| [IEEE Publication Recommender](https://publication-recommender.ieee.org/home) | IEEE publications; use journal/periodical results for this skill | Keywords; the service also offers article-file input | Publication scope, bibliometric information, OA availability, and publishing-time information; see [IEEE's guide](https://open.ieee.org/how-to-choose-the-right-publication-for-your-submission/). Conference results remain outside this skill's journal workflow. |

### Use these tools with the skill

1. Choose services appropriate to your field. Review the service's privacy information before sharing unpublished text or uploading a file.
2. Run the service yourself, or explicitly authorize the agent to use a named service if permitted browser access is available. Some interfaces require JavaScript or an authenticated session.
3. Supply a result export, shareable link, or copied journal list. Include the provider and run date, plus original scores if available. Export support varies; CSV is explicitly documented for Springer Nature.
4. Ask the skill to merge candidates, remove duplicates, and independently compare scope, methods, related papers, metrics, speed, and payable costs.

Example using results you have already obtained:

```text
Use $journal-suggester to compare the journals in my attached Springer
Nature CSV and copied Wiley results for the manuscript below.

Keep the original provider scores separate. Check official scope and
recent related publications, and report uncertain fees or timing clearly.

Article type: Original research
Abstract: [your abstract]
Results generated: [date, or unknown]
```

No automated adapters for these matching services are bundled in version 1. The skill uses available permitted access or supplied results. It does not submit manuscripts, initiate transfer services, or send your abstract to every provider automatically. Match scores are not acceptance probabilities, and first-decision figures do not necessarily measure external peer-review time.

## Privacy and manuscript handling

The skill defaults external literature searches to generic topical phrases. It asks for authorization before sending an unpublished abstract to a particular external matcher unless that service-specific authorization has already been provided. It does not automatically submit the abstract to every publisher.

Text supplied to your agent is still subject to that agent environment's data-handling arrangements. The skill does not establish confidentiality guarantees for external services. Recommendations do not authorize manuscript submission, editor contact, account registration, purchases, or persistent storage of a personal institution profile.

## Repository layout

```text
README.md
.gitignore
journal-suggester/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── scripts/
│   └── crossref.py
└── references/
    ├── evaluation.md
    ├── sources-and-integrations.md
    ├── apc-agreements.md
    └── output.md
tests/
├── test_crossref.py
└── skill-scenarios.md
```

Only the `journal-suggester/` folder is needed for installation. Keep the README and tests in the public repository to explain usage and support maintenance.

## License

No license has been selected for this repository yet. A `LICENSE` file should be added once the maintainer chooses the terms for reuse.
