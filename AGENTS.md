# AGENTS.md

Development guide for AI coding agents working in the **ClinicalTrials.gov core pipeline** repo. Read this before editing code.

This file is about **developing** the pipeline. For operating it (VM run procedure, GCS upload, UMLS release updates) see `docs/running-the-pipeline.md` and `docs/umls-update.md` — do not duplicate that here.

## What this repo is

A batch ETL pipeline (orchestrated by [`run_ct.sh`](run_ct.sh)) that runs numbered scripts `CT_01`–`CT_11` in sequence. Each step reads the previous step's TSV and writes the next one to `Intermediate_steps/CT_{batch}_{step}.tsv`. The data flows:

```
XML → 01 extract → 02 metamap condition → 03 metamap intervention
   → 05 dedup → 06 aggregate (evidence schema) → 07 NGS score
   → 08 title tag → 09 mesh (main) / 10 mesh (txt) → 11 text files
```

Step 04 is deprecated and not invoked (numbering jumps 03→05). Per-step detail lives in [`docs/pipeline-steps.md`](docs/pipeline-steps.md); the schema/consumer contract is in [`docs/outputs-and-downstream.md`](docs/outputs-and-downstream.md).

## Environment constraints (affect how you edit and verify)

- **You cannot run the pipeline here.** It needs the production VM (local MetaMap under `/tools/metamap_2020/...`, UMLS pickles under `/tools/metathesaurus_files/...`, GCS creds, network download). None are in git. Verify changes by static reasoning and syntax checks, not by executing `run_ct.sh`.
- **Mixed Python runtimes — match the file you edit.** The interpreter is pinned per step in `run_ct.sh` and the `*.sh` wrappers; the `#!/usr/bin/python` shebangs on some files are misleading, so trust the invocation, not the shebang.

  | Runtime | Files | Notes |
  |---------|-------|-------|
  | **Python 3 (assume 3.6+)** | `CT_01`, `CT_09`, `CT_10`, `CT_11`, `splitcsvk.py`, most of `misc/` | Use f-strings (`CT_11`, `misc/CT_umls_diff.py`). `splitcsvk.py` runs under py3 even though it feeds the py2.7 metamap steps. |
  | **Dual 2/3-compatible** | `CT_02`, `CT_03` | Run as `/usr/bin/python2.7`, but written portable: `from __future__ import print_function` + guarded `if sys.version_info[0] < 3: reload(sys); sys.setdefaultencoding(...)`. **Preserve that shim** — don't add hard-2.7-only idioms. |
  | **Hard Python 2.7** | `CT_05`, `CT_06`, `CT_07`, `CT_08` | Real 2.7 only: unconditional `reload(sys); sys.setdefaultencoding('utf-8')`, `print` statements, `raw_input`, `filter()` returning a list. These crash immediately under py3. |

  Do not "modernize" the 2.7 files to Python 3 unless explicitly asked — they run under a real 2.7 interpreter on the VM.
- **Dev host is Windows/PowerShell; scripts target Linux/bash.** `run_ct.sh` and the `*.sh` wrappers use `wget`, `unzip`, `netstat`, `ps`, `tar`, `gsutil`, `rm -rf`. They only run on the Linux VM — don't port or "fix" them for Windows.
- **Don't commit secrets or generated data.** `gcloud_service_account.json`, `xml_dumps/`, `Intermediate_steps/`, `txt-files/`, `*_logs/`, `*.tar.gz`, generated `*.tsv`. Large `cui2mesh_*.pkl` files already sit in the repo root; don't add new large binaries unprompted.

## TSV I/O conventions (the #1 source of bugs)

Every step reads and writes tab-separated files with **no quoting**. This is load-bearing — get it wrong and columns silently shift.

- Readers/writers are opened with `delimiter='\t', quoting=csv.QUOTE_NONE, quotechar=''` (`splitcsvk.py` also sets `escapechar='\\'`). Because nothing is quoted, **any literal tab, newline, `\r`, or `"` inside a field corrupts the row.** `CT_01_extraction.py` defends against this by stripping `\n\r\t` and replacing `"`→`'` on every field before writing; preserve that pattern anywhere you emit fields.
- Pipeline steps and most `misc/` readers set `csv.field_size_limit(58000000)` because some fields (e.g. `content_raw`) are very large. Keep it when adding a new reader.
- **Missing value is the string `'0'`** (Neo4j requirement), never `''`, `None`, or `NaN`. `XMLParser.default_value` and the aggregation defaults all use `'0'`.
- Encodings are inconsistent between steps: `CT_09`/`CT_10` read with `encoding='ISO-8859-1'`. Match the surrounding file rather than assuming UTF-8.

## Column contracts (trace these before touching a schema)

Two different addressing styles coexist — know which one a file uses:

- **Positional index** — `CT_06_aggregation.py` reads its 45-column input via hardcoded `src_*_ind = 0..44` constants (top of file) and writes a **121-column** header. If you add/remove/reorder any column in step 01 or 05, these integer indices break silently. Prefer **appending** new columns at the end.
- **Header name** — `CT_09`/`CT_10` locate columns with `row.index('cause_concept_cui')` etc. These tolerate reordering but break if you rename a column.

Key schema facts (set in `CT_06_aggregation.py`):

- **Cause = intervention, Effect = condition.** `cause_*` fields come from intervention columns; `effect_*` from condition columns. `connective_type='OBSERVATION'`, `sem_type='UNIDIRECTIONAL'`.
- **Row semantics:** one row per `condition × intervention` pair per trial (2 conditions × 3 interventions → up to 6 rows), produced in `CT_01` and deduped in `CT_05`.
- **Identity fields:** `data_source='8'`, `article_type='3'`, `article_uuid = {nct_id}_{batch_gen}_{parse_version}`, `primary_id = nct_id`. `batch_gen` and `parse_version` arrive as `sys.argv[3]`/`sys.argv[4]`.
- **Dedup key:** `CT_06` drops rows on a `source_hashcode` (sha256 of `article_hashcode + nct_id + intervention_cui + condition_cui + intervention_name + condition`, lowercased with spaces removed); `CT_05` dedups condition/intervention pairs. Changing the fields that feed the hash changes dedup behavior.
- The step-01 header intentionally repeats some names (`overall_status`, `source`) at different indices — don't "dedupe" the header.

## Step internals worth knowing

- **`CT_01_extraction.py` (py3):** walks `xml_dumps/`, parses via `utils/xml_parser.py` driven by `config/rules.json` (XPath rules; `plural` rules produce lists). Splits compound intervention names on `' + '` and `' or '`. Emits 45 columns with MetaMap columns pre-initialized to `'0'`; asserts row length matches the header.
- **`CT_02`/`CT_03` metamap (py2.7):** the `.sh` wrapper splits input into `NUM_PROCS=10` chunks with `splitcsvk.py`, runs up to 10 parallel `python2.7` workers, caches each chunk as a `.pkl` in `metamap_*_cache/`, then merges with `head -1` + `tail -n+2`. The worker takes `input output cache.pkl log.txt`. Allowed semantic categories, CUI blacklist (`utils/Universal_statex_blacklist.xlsx`), score modifiers, and MetaMap `-Z`/`-V` version args are **hardcoded near the top of the worker**. Concept overrides live in `utils/CT_conditions_manual_remaps.tsv` / `utils/CT_interventions_manual_remaps.tsv`.
- **`CT_06`–`CT_08` (py2.7):** aggregation builds the HTML `content_raw` and the full evidence schema; scoring/tagging append columns. Version-like constants (`data_source`, `parse_version`, weights) are hardcoded here and in `CT_07`.
- **`CT_09`/`CT_10` (py3):** map `cause`/`effect` CUIs to MeSH via a `cui2mesh_*.pkl` (path passed as `sys.argv[3]`); `09` writes term names into `article_mesh_terms`, `10` writes `MESH_ID#####TERM` pairs. `CT_11` re-reads source XML to build one `{article_uuid}.txt` per trial.

## Gotchas

- **`CT_06_aggregation.py` and `CT_08_title_tagging_agg.py` contain `raw_input('wait')`** in empty-field checks. If a field is blank they will **block forever** on the VM. If you touch those scripts, understand this before assuming a hang is something else.
- **`splitcsvk.py` silently drops rows** whose column count ≠ header (it just increments a counter). Malformed extraction rows disappear here.
- **No test suite, no CI, no linter config.** Validation is manual. The QA/sanity scripts in `misc/` (`conditions_sanity_check.py`, `interventions_sanity_check.py`, `CT_umls_diff.py`, `find_missing_cui2cat.py`, `CT_stats.py`) are the intended tooling — extend those rather than inventing new ones.
- **Manual remap TSVs are BIS-curated** (`utils/CT_conditions_manual_remaps.tsv` ~396 rows, `utils/CT_interventions_manual_remaps.tsv` ~4,055 rows). Don't bulk-edit or reformat; they are request-string → CUI overrides with notes.

## Module map

| Path | Role |
|------|------|
| `run_ct.sh` | Orchestrator: cleanup → download → steps 01–11 → archive → upload → stats |
| `CT_0X_*.py` / `CT_0X_*.sh` | Numbered steps (`.sh` wrappers parallelize the metamap steps) |
| `CT_01_extraction_old.py` | Legacy extraction; **not** used by `run_ct.sh` |
| `splitcsvk.py` | Splits a TSV into 10 chunks for parallel metamap |
| `config/rules.json` | XPath extraction rules consumed by `utils/xml_parser.py` |
| `utils/xml_parser.py` | Generic rule-driven XML field extractor |
| `utils/querying_mappings.py`, `global_term_mappings.py`, `global_chem_mappings.py`, `prohibited_words.py` | Term normalization / filtering used by metamap steps |
| `utils/timeout.py` | Timeout decorator for metamap calls |
| `utils/CT_*_manual_remaps.tsv` | Curated request-string → CUI overrides |
| `misc/*` | Dictionary builders + QA/sanity/diff/stats scripts |
| `cui2mesh_*.pkl`, `umls_statex.xlsx` | Data assets loaded at runtime (steps 09/10 and metamap) |
| `docs/` | Authoritative behavior/ops documentation |

## Working effectively

- **Read the whole target script and its neighbors first.** Grep for the column name/index and the constant you're changing across all `CT_*` files before editing.
- **Prefer minimal, in-style edits.** These files predate modern formatting; don't reformat surrounding code.
- **When you change pipeline behavior, update the matching `docs/` file in the same change.**
- **Comments:** only for non-obvious intent (e.g. why a column index or a `'0'` default is required). Don't narrate code.
- Changes to `{batch}_ctgov_main.tsv` columns/semantics are **breaking** for the Neo4j and NGS consumers — see [`docs/outputs-and-downstream.md`](docs/outputs-and-downstream.md) before touching the schema.
