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
- Uses available publisher-suggester results or user-provided exports as discovery leads, followed by independent verification.

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

## Development and validation

Run the offline helper tests from the repository root:

```bash
python3 -B -m unittest discover -s tests -v
```

The suite covers metadata handling, request construction, input validation, bounded retries, error handling, and TLS verification. [Behavioral scenarios](tests/skill-scenarios.md) support manual evaluation of the skill's decisions. These checks do not quantify recommendation accuracy or demonstrate compatibility with every agent or Python version.

For contributions, use synthetic or already-public examples. Include the source and access date for proposed data-source changes. Keep manuscripts, personal details, credentials, downloaded PDFs, and generated retrieval runs out of commits.

## Publishing this repository

Include `README.md`, `.gitignore`, the entire `journal-suggester/` folder, and the two reusable test files. From the repository root, stage that explicit set:

```bash
git add README.md .gitignore journal-suggester/ tests/test_crossref.py tests/skill-scenarios.md
git diff --cached --stat
```

Review the staged files before committing and pushing. Local PDFs, generated ZIP packages, and `tests/runs/` are excluded by `.gitignore`. A downloadable skill ZIP may be attached to a GitHub Release rather than committed alongside its source.

Publishing this source repository does not automatically create a plugin-directory listing.

## License

No license has been selected for this repository yet. A `LICENSE` file should be added once the maintainer chooses the terms for reuse.
