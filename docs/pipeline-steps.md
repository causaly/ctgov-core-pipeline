# Pipeline Steps (Detailed Reference)

Step-by-step reference for each stage of the ClinicalTrials.gov core pipeline. The orchestrator is [`run_ct.sh`](../run_ct.sh); all intermediate TSVs land in `Intermediate_steps/CT_{batch}_{step}.tsv`.

**Batch parameter:** `batch_gen` = 8-digit `YYYYMMDD` (e.g. `20260517`).

---

## Overview

| Step | Script | Python | Input TSV | Output TSV |
|------|--------|--------|-----------|------------|
| 0 | `run_ct.sh` (download) | bash | — | `xml_dumps/` |
| 01 | `CT_01_extraction.py` | 3 | XML folders | `CT_{batch}_01.tsv` |
| 02 | `CT_02_metamap_condition.sh` → `.py` | 3 + 2.7 | `_01` | `CT_{batch}_02.tsv` |
| 03 | `CT_03_metamap_intervention.sh` → `.py` | 3 + 2.7 | `_02` | `CT_{batch}_03.tsv` |
| 04 | *(deprecated, not run)* | — | — | — |
| 05 | `CT_05_deduplication.py` | 2.7 | `_03` | `CT_{batch}_05.tsv` |
| 06 | `CT_06_aggregation.py` | 2.7 | `_05` | `CT_{batch}_06.tsv` |
| 07 | `CT_07_ngs_scoring.py` | 2.7 | `_06` | `CT_{batch}_07.tsv` |
| 08 | `CT_08_title_tagging_agg.py` | 2.7 | `_07` | `CT_{batch}_08.tsv` |
| 09 | `CT_09_mesh_generation.py` | 3 | `_08` | `CT_{batch}_09.tsv` |
| 10 | `CT_10_mesh_generation_txt_files.py` | 3 | `_08` | `CT_{batch}_10.tsv` |
| 11 | `CT_11_text_generation.py` | 3 | `_10` + XML | `txt-files/*.txt` |

Step 04 (`CT_04_COVID_replacement.py`) is deprecated and not invoked by `run_ct.sh`. Numbering jumps from 03 → 05.

---

## Step 0 — Download and unzip

**Where:** `run_ct.sh` lines 27–38

**What:**
1. Cleans previous run artifacts (`Intermediate_steps/`, `xml_dumps/`, `txt-files/`, metamap caches, etc.)
2. Downloads `https://classic.clinicaltrials.gov/AllAPIXML.zip`
3. Unzips into `xml_dumps/` (folders named `NCTxxxxx/`, each containing one XML file)
4. Archives the zip as `{batch}_xml_dumps.zip` in the repo root

**Output:** `xml_dumps/NCT*/{NCT_ID}.xml`, `{batch}_xml_dumps.zip`

---

## Step 01 — XML extraction

| | |
|---|---|
| **Script** | [`CT_01_extraction.py`](../CT_01_extraction.py) |
| **Parser** | [`utils/xml_parser.py`](../utils/xml_parser.py) + [`config/rules.json`](../config/rules.json) |
| **Python** | 3 |
| **Invocation** | `python3 CT_01_extraction.py $PWD/xml_dumps $PWD/Intermediate_steps/CT_${batch}_01.tsv` |

**What:**
- Walks all XML files under `xml_dumps/`
- Extracts predefined fields via XPath rules in `config/rules.json`
- Expands each trial to **one row per condition × intervention pair** (or condition-only / intervention-only when one side is missing)
- Splits compound intervention names on `' + '` and `' or '`
- Initializes MetaMap columns to `'0'` (Neo4j default for missing values)

**Example:** 2 conditions × 3 interventions → 6 rows for one NCT ID.

**Output columns (45):** `filename`, `official_title`, `brief_title`, `condition`, `cond_mm_request`, `condition_concept`, `condition_cui`, `condition_categories`, `condition_all_mm`, `intervention_type`, `intervention_name`, `intervention_mm_request`, `intervention_concept`, `intervention_cui`, `intervention_categories`, `intervention_all_mm`, `intervention_description`, trial metadata (`overall_status`, `phase`, `study_type`, eligibility, sponsors, dates, MeSH terms, outcomes, `references`, etc.), `nct_id`.

---

## Step 02 — Condition MetaMap

| | |
|---|---|
| **Wrapper** | [`CT_02_metamap_condition.sh`](../CT_02_metamap_condition.sh) |
| **Worker** | [`CT_02_metamap_condition.py`](../CT_02_metamap_condition.py) |
| **Python** | 3 (`splitcsvk.py`) + 2.7 (worker) |
| **Invocation** | `bash CT_02_metamap_condition.sh <input> <output>` |

**Parallelism:** Splits input into 10 chunks via [`splitcsvk.py`](../splitcsvk.py); runs up to 10 parallel worker processes; merges chunk TSVs. Per-chunk pickle caches in `metamap_conditions_cache/`.

**MetaMap command (conditions):**
```
/tools/metamap_2020/public_mm/bin/metamap -Z 2023AB -V custom2025AB -Cz -R <source list> --sldi --prune 15 --XMLf
```

**Allowed semantic categories:** `DISO`, `T004`, `T005`, `T007`, `T204`, `T032`, `T055`, `T061`, `T043`, `T116`, `T129`

**Key logic:**
- `read_umls_catcodes()` reads semantic type priorities from `umls_statex.xlsx`
- `get_best_record()` picks highest-priority allowed semantic type from MetaMap XML response
- `heuristic_fixes()` applies post-processing rules
- Manual overrides: [`utils/CT_conditions_manual_remaps.tsv`](../utils/CT_conditions_manual_remaps.tsv)
- Blacklisted CUIs: [`utils/Universal_statex_blacklist.xlsx`](../utils/Universal_statex_blacklist.xlsx), loaded inline in the worker script
- Term normalization: [`utils/querying_mappings.py`](../utils/querying_mappings.py), [`utils/global_term_mappings.py`](../utils/global_term_mappings.py)

**Fills columns:** `condition_concept`, `condition_cui`, `condition_categories`, `condition_all_mm`

---

## Step 03 — Intervention MetaMap

| | |
|---|---|
| **Wrapper** | [`CT_03_metamap_intervention.sh`](../CT_03_metamap_intervention.sh) |
| **Worker** | [`CT_03_metamap_intervention.py`](../CT_03_metamap_intervention.py) |
| **Python** | 3 (`splitcsvk.py`) + 2.7 (worker) |
| **Invocation** | `bash CT_03_metamap_intervention.sh <input> <output>` |

Same 10-chunk parallel pattern as step 02. Caches in `metamap_interventions_cache/`.

**Allowed semantic categories:** `CHEM`, `T168`, `LIVB`, `PROC`, `T074`, `T203`, `T025`

**Manual overrides:** [`utils/CT_interventions_manual_remaps.tsv`](../utils/CT_interventions_manual_remaps.tsv)

**Fills columns:** `intervention_concept`, `intervention_cui`, `intervention_categories`, `intervention_all_mm`

**MetaMap servers:** `run_ct.sh` starts `skrmedpostctl` (port 1795) and `wsdserverctl` (port 5554) if not already running, before steps 02 and 03.

---

## Step 04 — COVID replacement (deprecated)

**Script:** `CT_04_COVID_replacement.py` — **not in repo, not invoked.**

Previously replaced COVID-19 strings in cause/effect fields. Removed from the pipeline.

---

## Step 05 — Post-MetaMap deduplication

| | |
|---|---|
| **Script** | [`CT_05_deduplication.py`](../CT_05_deduplication.py) |
| **Python** | 2.7 |
| **Invocation** | `/usr/bin/python2.7 CT_05_deduplication.py <input> <output>` |

**What:** Removes duplicate rows introduced by XML duplication or MetaMap returning identical concepts for different strings. Deduplicates by unique `nct_id` + condition/intervention CUI (or raw text when CUI is `'0'`).

---

## Step 06 — Aggregation (Neo4j evidence schema)

| | |
|---|---|
| **Script** | [`CT_06_aggregation.py`](../CT_06_aggregation.py) |
| **Python** | 2.7 |
| **Invocation** | `/usr/bin/python2.7 CT_06_aggregation.py <input> <output> $batch_gen 0.6` |

**Parameters:**
- `$batch_gen` — batch date (`YYYYMMDD`)
- `0.6` — `parse_version` (hardcoded in `run_ct.sh`)

**What:**
- Maps **intervention → cause**, **condition → effect** (clinical trial evidence convention)
- Produces **121-column** Neo4j/evidence schema
- Builds HTML `content_raw` from trial metadata
- Computes hashcodes for evidence rows

**Key output fields:**

| Field | Value | Meaning |
|-------|-------|---------|
| `data_source` | `8` | ClinicalTrials.gov source ID |
| `article_type` | `3` | Clinical trial article type |
| `connective_type` | `OBSERVATION` | Evidence connective |
| `sem_type` | `UNIDIRECTIONAL` | Relationship directionality |
| `article_uuid` | `{nct_id}_{batch_gen}_{parse_version}` | Unique trial batch ID |
| `batch_generation` | `{batch_gen}` | Release batch date |
| `parse_version` | `0.6` | Pipeline code version |
| `primary_id` | `{nct_id}` | Trial identifier (already `NCT…`-prefixed) |

Default missing value throughout: `'0'` (Neo4j requirement).

---

## Step 07 — NGS evidence scoring

| | |
|---|---|
| **Script** | [`CT_07_ngs_scoring.py`](../CT_07_ngs_scoring.py) |
| **Python** | 2.7 |
| **Invocation** | `/usr/bin/python2.7 CT_07_ngs_scoring.py <input> <output>` |

**UMLS dictionaries** (loaded from `/tools/metathesaurus_files/2025AB_data/`):
- `2025AB_atoms.pkl2` — MRCONSO entry terms
- `2025AB_parents.pkl2` / `2025AB_children.pkl2` — MRREL hierarchy
- `2025AB_cui_to_cat.pkl2` — MRSTY semantic categories

**What:** Scores concept presence in article title and MeSH terms using UMLS atoms and parent/child hierarchy. Tags concepts in titles as `<concept cui=... cat=...>`. Adds a flat `+0.1` bonus when `article_section` is `Results/Findings` or `Conclusion/Discussion` (not atom matching on conclusion text).

**Adds columns:** `ngs_score`, `article_title_evidence_tag`, `final_ngs_score`

**Scoring weights:** title=1.0, title-related=0.5, MeSH=0.5, MeSH-related=0.25, conclusion=0.1

---

## Step 08 — Title tagging aggregation

| | |
|---|---|
| **Script** | [`CT_08_title_tagging_agg.py`](../CT_08_title_tagging_agg.py) |
| **Python** | 2.7 |
| **Invocation** | `/usr/bin/python2.7 CT_08_title_tagging_agg.py <input> <output>` |

**What:** Aggregates per-`article_uuid` concept tags from all evidence rows into a single tagged title.

**Adds column:** `final_aggregated_title_tagged`

---

## Step 09 — MeSH generation (main evidence file)

| | |
|---|---|
| **Script** | [`CT_09_mesh_generation.py`](../CT_09_mesh_generation.py) |
| **Python** | 3 |
| **Invocation** | `python3 CT_09_mesh_generation.py <input> <output> $PWD/cui2mesh_2025AB_merged_2023AB.pkl` |

**What:** Maps condition and intervention CUIs to MeSH term **names** via the CUI→MeSH pickle. Populates `article_mesh_terms` with term names only (no MeSH IDs).

**Output:** `CT_{batch}_09.tsv` — copied to `{batch}_ctgov_main.tsv` (canonical Neo4j/BQ artifact).

---

## Step 10 — MeSH generation (txt files, with IDs)

| | |
|---|---|
| **Script** | [`CT_10_mesh_generation_txt_files.py`](../CT_10_mesh_generation_txt_files.py) |
| **Python** | 3 |
| **Invocation** | `python3 CT_10_mesh_generation_txt_files.py <input> <output> $PWD/cui2mesh_2025AB_merged_2023AB.pkl` |

**Input:** Step 08 output (not step 09).

**What:** Same CUI→MeSH mapping but populates `article_mesh_terms` with `MESH_ID#####MESH_TERM` pairs for enhanced frontend indexing in the text files.

---

## Step 11 — Text file generation

| | |
|---|---|
| **Script** | [`CT_11_text_generation.py`](../CT_11_text_generation.py) |
| **Python** | 3 |
| **Invocation** | `python3 CT_11_text_generation.py <tsv> $PWD/xml_dumps txt-files` |

**What:**
- Re-reads source XML for full abstract content (brief/official title, interventions, summaries, eligibility, arm groups, keywords)
- Writes one `{article_uuid}.txt` per unique trial in `txt-files/`
- NGS-style format with metadata headers + MeSH blocks

**Post-step:** `run_ct.sh` archives `txt-files/` as `{batch}_ctgov_text.tar.gz`.

---

## Post-pipeline (in `run_ct.sh`)

| Action | Output |
|--------|--------|
| GCS upload | `gs://prd-ngs-ctgov/{batch}/` (see [outputs-and-downstream.md](outputs-and-downstream.md)) |
| Stats | `{batch}_stats.txt` via [`misc/CT_stats.py`](../misc/CT_stats.py) |

---

## Config and utility files

| File | Role |
|------|------|
| [`config/rules.json`](../config/rules.json) | XPath extraction rules for CT.gov XML |
| [`utils/CT_conditions_manual_remaps.tsv`](../utils/CT_conditions_manual_remaps.tsv) | Manual condition string→CUI overrides |
| [`utils/CT_interventions_manual_remaps.tsv`](../utils/CT_interventions_manual_remaps.tsv) | Manual intervention string→CUI overrides |
| `umls_statex.xlsx` | Semantic type priorities (repo root) |
| `utils/Universal_statex_blacklist.xlsx` | CUI blacklist (repo root) |
| `cui2mesh_2025AB_merged_2023AB.pkl` | CUI→MeSH mapping (repo root on VM) |
