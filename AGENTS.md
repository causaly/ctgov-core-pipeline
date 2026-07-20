# AGENTS.md

Guidance for AI coding agents working in the **ClinicalTrials.gov core pipeline** repo. Read this before editing.

## What this repo is

A batch ETL pipeline that downloads ClinicalTrials.gov XML, maps conditions and interventions to UMLS concepts via MetaMap, aggregates them into a Neo4j evidence schema, scores them for NGS search, and produces text abstracts for indexing. It emits a canonical evidence TSV and a text tarball to GCS for downstream consumers (Neo4j knowledge graph, NGS search).

The orchestrator is [`run_ct.sh`](run_ct.sh). It runs numbered scripts `CT_01`–`CT_11` sequentially. Entry point: `./run_ct.sh YYYYMMDD`.

Start with [`docs/overview.md`](docs/overview.md). The `docs/` folder is the source of truth for behavior:
- [`docs/pipeline-steps.md`](docs/pipeline-steps.md) — per-step scripts, inputs, outputs, logic
- [`docs/running-the-pipeline.md`](docs/running-the-pipeline.md) — VM run procedure, prerequisites, troubleshooting
- [`docs/umls-update.md`](docs/umls-update.md) — UMLS release update procedure
- [`docs/outputs-and-downstream.md`](docs/outputs-and-downstream.md) — GCS layout, evidence contract, consumers

**When you change pipeline behavior, update the relevant `docs/` file in the same change.**

## Critical constraints (read before running anything)

- **You cannot run the full pipeline locally.** It requires a production GCP VM (`prd-pipeline-ct-gov`) with a local MetaMap install (`/tools/metamap_2020/...`), UMLS scoring pickles (`/tools/metathesaurus_files/...`), GCS service-account credentials, and network downloads. None of these are in git. Do not attempt to `./run_ct.sh` or start MetaMap servers in this workspace.
- **The dev host is Windows 11 / PowerShell; the pipeline targets Linux/bash.** `run_ct.sh` and the `.sh` wrappers use `wget`, `unzip`, `netstat`, `gsutil`, `tar`, `rm -rf`. Do not "port" these to PowerShell or "fix" them — they are meant to run on the Linux VM. Treat shell scripts as Linux artifacts.
- **Mixed Python runtimes.** Steps `01`, `09`, `10`, `11` are **Python 3**. Steps `02`–`08` are **Python 2.7** (invoked as `/usr/bin/python2.7`). Do not modernize the Python 2.7 scripts to Python 3 syntax unless explicitly asked — they run under a real 2.7 interpreter on the VM. Match the existing runtime of whatever file you edit.
- **Do not commit secrets or large data.** `gcloud_service_account.json`, downloaded XML, `Intermediate_steps/`, `txt-files/`, `*_logs/`, `*.tar.gz`, and generated `*.tsv` outputs must never be committed. Large `*.pkl` mapping files already live in the repo root (`cui2mesh_*.pkl`); do not add new large binaries without being asked.

## Repo layout

| Path | Role |
|------|------|
| `run_ct.sh` | Orchestrator; runs steps 01–11, uploads to GCS, writes stats |
| `CT_0X_*.py` / `CT_0X_*.sh` | Numbered pipeline steps (see `docs/pipeline-steps.md`) |
| `CT_04_COVID_replacement.py` | **Deprecated, not in repo, not invoked** — numbering skips 03→05 |
| `CT_01_extraction_old.py` | Legacy extraction; not used by `run_ct.sh` |
| `splitcsvk.py` | Splits input into 10 chunks for parallel MetaMap (steps 02/03) |
| `config/rules.json` | XPath extraction rules for CT.gov XML (step 01) |
| `utils/` | Parsers, term-mapping dicts, manual remap TSVs, blacklists |
| `misc/` | Dictionary builders and QA/sanity scripts (UMLS updates, stats, diffs) |
| `cui2mesh_*.pkl` | CUI→MeSH mapping pickles (steps 09/10) |
| `umls_statex.xlsx` | Semantic type priorities |
| `docs/` | Authoritative documentation |

## Data-flow conventions you must preserve

These are load-bearing invariants. Breaking them silently corrupts the knowledge graph or breaks the Neo4j import.

- **Column order matters.** Scripts read/write TSVs by positional index in many places, not by header name. If you add, remove, or reorder a column in one step, trace every downstream step (and `docs/outputs-and-downstream.md`) that indexes into it. Prefer appending columns at the end.
- **Missing value is the string `'0'`.** Neo4j import requires it. Do not use empty string, `None`, or `NaN` for missing fields.
- **Cause/effect mapping:** intervention → **cause**, condition → **effect** (`connective_type=OBSERVATION`, `sem_type=UNIDIRECTIONAL`). Set in step 06.
- **Row semantics:** one row per `condition × intervention` pair per trial (2 conditions × 3 interventions → up to 6 rows, after step 05 dedup).
- **Identity fields:** `data_source=8` (CT.gov), `article_type=3`, `article_uuid = {nct_id}_{batch_gen}_{parse_version}`, `primary_id = NCT{nct_id}`.
- **Intermediate files** follow `Intermediate_steps/CT_{batch}_{step}.tsv`; the canonical output is `{batch}_ctgov_main.tsv` (a copy of the step-09 TSV).

## Version constants (hardcoded, scattered)

There is no central config for versions — they are hardcoded across files. When bumping a UMLS release, follow [`docs/umls-update.md`](docs/umls-update.md) exactly and update **all** of these:

| Constant | Current | Where |
|----------|---------|-------|
| MetaMap UMLS (`-Z`) | `2023AB` | `CT_02_metamap_condition.py`, `CT_03_metamap_intervention.py` |
| MetaMap custom vocab (`-V`) | `custom2025AB` | same two scripts |
| Scoring pickle dir | `/tools/metathesaurus_files/2025AB_data/` | `CT_07_ngs_scoring.py` (~line 30) |
| CUI→MeSH pickle | `cui2mesh_2025AB_merged_2023AB.pkl` | `run_ct.sh` (steps 09/10) |
| `parse_version` | `0.6` | `run_ct.sh` (passed to step 06) |
| `data_source` | `8` | `CT_06_aggregation.py` |

## Working effectively as an agent

- **Verify before editing:** these scripts are old and lightly tested. Read the whole target script and its callers/downstream consumers before changing logic. Grep for column indices and the constants above.
- **No test suite / CI.** There are no automated tests and no local run path. Validate changes by reasoning about column contracts and, where possible, by static checks (syntax, imports) appropriate to the file's Python version. The real validation happens on the VM against a batch; call out that a VM run is needed to confirm.
- **Sanity/QA scripts** in `misc/` (`conditions_sanity_check.py`, `interventions_sanity_check.py`, `CT_umls_diff.py`, `find_missing_cui2cat.py`, `CT_stats.py`) are the intended validation tooling — reference/extend these rather than inventing new ones.
- **Manual remaps** (`utils/CT_conditions_manual_remaps.tsv` ~396 rows, `utils/CT_interventions_manual_remaps.tsv` ~4,055 rows) are curated by BIS during UMLS QA. Do not bulk-edit or reformat them; they are request-string → CUI overrides with notes.
- **Match existing style.** These files predate modern linting; there is no formatter config. Keep edits minimal and consistent with the surrounding file rather than reformatting.
- **Comments:** only add comments that explain non-obvious intent (e.g. why a column index or a `'0'` default is required). Do not narrate code.

## Common tasks → where to look

| Task | Start here |
|------|-----------|
| Add/change an extracted XML field | `config/rules.json` + `utils/xml_parser.py` + `CT_01_extraction.py`, then trace downstream column indices |
| Adjust concept mapping / allowed semantic types | `CT_02_*` (conditions) / `CT_03_*` (interventions) + `utils/` mappings + manual remap TSVs |
| Change evidence schema / Neo4j columns | `CT_06_aggregation.py` (121-col schema) + `docs/outputs-and-downstream.md` |
| Change NGS scoring | `CT_07_ngs_scoring.py` (weights: title=1.0, title-related=0.5, MeSH=0.5, MeSH-related=0.25, conclusion=0.1) |
| Change MeSH output | `CT_09` (term names) / `CT_10` (`MESH_ID#####TERM`) + cui2mesh pickle |
| Change text-file output | `CT_11_text_generation.py` |
| Bump UMLS version | `docs/umls-update.md` (full checklist) |
| Change run/upload/stats flow | `run_ct.sh` + `docs/running-the-pipeline.md` + `misc/CT_stats.py` |

## Downstream contract (don't break)

Outputs land in `gs://prd-ngs-ctgov/{batch}/`:
- `{batch}_ctgov_main.tsv` → `neo4j-loading` and `ngs-upload-pipeline` (`evidence_ct`)
- `{batch}_ctgov_text.tar.gz` → `ngs-upload-pipeline` (`abstracts_nct`)
- `{batch}_xml_dumps.zip` → modern `ctgov` embeddings pipeline

Changes to the main TSV's columns/semantics are breaking changes for Neo4j and NGS. See [`docs/outputs-and-downstream.md`](docs/outputs-and-downstream.md) before touching the schema.
