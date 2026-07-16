# UMLS Update Procedure

Step-by-step procedure for updating the pipeline to a new UMLS release. This affects MetaMap concept mapping (steps 02–03), NGS scoring dictionaries (step 07), and MeSH generation (steps 09–10).

**Confluence reference:** [UMLS update process](https://causaly.atlassian.net/wiki/spaces/DaST/pages/2710142978/UMLS+update+process)

---

## Overview

A UMLS update involves three phases:

1. **MetaMap + QA** — run steps 01–03 with old and new UMLS versions, diff, get BIS feedback, update manual remaps
2. **Rebuild scoring dictionaries** — atoms, parents, children, cui_to_cat pickles for step 07
3. **Rebuild CUI→MeSH mapping** — cui2mesh pickle for steps 09–10

Reference commits for prior updates:
- MetaMap custom vocab `custom2025AB`: [e648641](https://github.com/causaly/ctgov-core-pipeline/commit/e648641dd55ac199ba3bce250eda237bfc381d93)
- Scoring pickles + cui2mesh paths: [b94e80a](https://github.com/causaly/ctgov-core-pipeline/commit/b94e80a6cc1f57c32e8f9c46a09602feb1ce95a4)

---

## Phase 1 — Update MetaMap + QA

### 1.1 Run pipeline through step 03 for both versions

Run the pipeline **only through step 03** (`CT_03_metamap_intervention.sh`) for:
- The **current** UMLS version (baseline)
- The **new** UMLS version

For the new version:
1. Update the local MetaMap installation to use the new UMLS resources
2. Change the `-Z` (UMLS year) and `-V` (custom vocab) arguments in both:
   - [`CT_02_metamap_condition.py`](../CT_02_metamap_condition.py) (line ~516, `MMQUERY_MMSH`)
   - [`CT_03_metamap_intervention.py`](../CT_03_metamap_intervention.py) (equivalent line)

Current values: `-Z 2023AB -V custom2025AB`

### 1.2 Generate diff spreadsheet

Run [`misc/CT_umls_diff.py`](../misc/CT_umls_diff.py) with the old and new step-03 outputs:

```bash
python misc/CT_umls_diff.py <old_step03.tsv> <new_step03.tsv> <output.xlsx>
```

Produces an Excel file with two sheets:
- `conditions_changed` — condition request strings that map to a different concept (including newly mapped / newly unmapped)
- `interventions_changed` — same for interventions

Rows are sorted by frequency (most frequent changes first).

### 1.3 BIS QA review

Hand the diff spreadsheet to BIS for review. Typical effort: **1–3 days** for a single BIS.

BIS does not exhaustively QA the entire diff — they rely on the frequency sort to evaluate the most impactful changes.

### 1.4 Update manual remap files

Based on BIS feedback, update:
- [`utils/CT_conditions_manual_remaps.tsv`](../utils/CT_conditions_manual_remaps.tsv) (~396 overrides)
- [`utils/CT_interventions_manual_remaps.tsv`](../utils/CT_interventions_manual_remaps.tsv) (~4,055 overrides)

Each row maps a request string to a CUI, with notes on UMLS retirements/mergers.

### 1.5 Re-run and verify

1. Re-run step 03 with the **new** UMLS version and updated remap files
2. Re-generate the diff (new output vs old UMLS output)
3. Hand back to BIS for verification (~0.5 day)

---

## Phase 2 — Rebuild scoring dictionaries

These pickles are used by step 07 (`CT_07_ngs_scoring.py`). They must be rebuilt for each UMLS release.

**Deploy location:** `/tools/metathesaurus_files/<version>/` on `prd-pipeline-ct-gov`

Build both `.pkl` and `.pkl2` variants (`.pkl2` for Python 2.7 compatibility in step 07).

### 2.1 Atoms dictionary

```bash
python misc/atoms_dict_build.py <MRCONSO.RRF> <output_path>/<version>_atoms.pkl
```

Input: new UMLS `MRCONSO.RRF` file.

### 2.2 Parents and children dictionaries

```bash
python misc/parent_child_dict_build.py <MRREL.RRF> <output_path>/<version>_parents.pkl <output_path>/<version>_children.pkl
```

Input: new UMLS `MRREL.RRF` file. Extracts `par`, `chd`, `rb`, `rn` relationship types.

### 2.3 CUI-to-category dictionary

```bash
python misc/cui_to_cat_dict_build.py <MRSTY.RRF> utils/Universal_statex_blacklist.xlsx <output_path>/<version>_cui_to_cat.pkl
```

Input: new UMLS `MRSTY.RRF` + semantic type blacklist spreadsheet.

### 2.4 Verify no missing CUIs

Run [`misc/find_missing_cui2cat.py`](../misc/find_missing_cui2cat.py) against the new UMLS step-03 output:

```bash
python misc/find_missing_cui2cat.py <new_step03.tsv>
```

Update lines 11 and 13 of the script to point to your new `cui_to_cat.pkl2` file.

If missing CUIs are printed:
1. Look up their category codes in UMLS browser
2. Add them to `missing_cuis_dict` in [`misc/cui_to_cat_dict_build.py`](../misc/cui_to_cat_dict_build.py) (line ~71)
3. Re-run `cui_to_cat_dict_build.py`
4. Re-verify with `find_missing_cui2cat.py` until no missing CUIs remain

**Critical:** Skipping this step will cause step 07 to stall and fail to complete.

### 2.5 Update hardcoded paths in step 07

Update `dictionaryDir` and filenames in [`CT_07_ngs_scoring.py`](../CT_07_ngs_scoring.py) (line ~30):

```python
dictionaryDir = '/tools/metathesaurus_files/<new_version>/'
# filenames: <version>_atoms.pkl2, <version>_parents.pkl2, etc.
```

See commit [b94e80a](https://github.com/causaly/ctgov-core-pipeline/commit/b94e80a6cc1f57c32e8f9c46a09602feb1ce95a4) for the pattern.

---

## Phase 3 — Rebuild CUI→MeSH mapping

Used by steps 09 and 10.

### 3.1 Build new cui2mesh pickle

```bash
python misc/cui2mesh_dict_build.py <MRCONSO.RRF> <new_cui2mesh.pkl> <previous_cui2mesh.pkl> <merged_cui2mesh.pkl>
```

Arguments:
1. New `MRCONSO.RRF` (filters `source=MSH`, `ts=P`, `ts2=PF`)
2. Output path for new pickle (e.g. `cui2mesh_2026AB.pkl`)
3. Previous merged pickle (e.g. `cui2mesh_2025AB_merged_2023AB.pkl`) — for coverage continuity
4. Output path for merged pickle (e.g. `cui2mesh_2026AB_merged_2025AB.pkl`)

The **merged** file (argument 4) is the one committed to the repo root and used in production.

### 3.2 Update `run_ct.sh`

Update the cui2mesh pickle path in steps 09 and 10 (lines ~103 and ~108):

```bash
python3 CT_09_mesh_generation.py ... $PWD/cui2mesh_<new_version>_merged_<prev_version>.pkl
python3 CT_10_mesh_generation_txt_files.py ... $PWD/cui2mesh_<new_version>_merged_<prev_version>.pkl
```

---

## Sanity-check scripts

After a UMLS update, these scripts help validate output quality:

| Script | Purpose |
|--------|---------|
| [`misc/conditions_sanity_check.py`](../misc/conditions_sanity_check.py) | Validates condition metamap cache consistency |
| [`misc/interventions_sanity_check.py`](../misc/interventions_sanity_check.py) | Validates intervention metamap cache consistency |
| [`misc/CT_umls_diff.py`](../misc/CT_umls_diff.py) | Compares two pipeline outputs (any version pair) |
| [`misc/find_missing_cui2cat.py`](../misc/find_missing_cui2cat.py) | Finds CUIs missing from cui_to_cat dictionary |

---

## Checklist

- [ ] Install new UMLS release on VM
- [ ] Update MetaMap custom vocab
- [ ] Update `-Z` / `-V` in metamap scripts (steps 02–03)
- [ ] Run steps 01–03 for old and new versions
- [ ] Generate diff spreadsheet (`CT_umls_diff.py`)
- [ ] BIS QA review (1–3 days)
- [ ] Update manual remap TSVs
- [ ] Re-run + re-diff for BIS verification
- [ ] Rebuild atoms/parents/children/cui_to_cat pickles
- [ ] Verify no missing CUIs (`find_missing_cui2cat.py`)
- [ ] Update `CT_07_ngs_scoring.py` dictionary paths
- [ ] Rebuild cui2mesh pickle (merged)
- [ ] Update `run_ct.sh` cui2mesh paths (steps 09–10)
- [ ] Run full pipeline (`./run_ct.sh YYYYMMDD`)
- [ ] Update [CTgov run log](https://causaly.atlassian.net/wiki/spaces/DaST/pages/409698422) with new stats
- [ ] Notify `context-release-channel`
