# ClinicalTrials.gov pipeline

This guide describes how to obtain, extract, process, and load ClinicalTrials.gov records into Neo4j.

---

## I. Data Source

The data is obtained from ClinicalTrials.gov.

Current approach downloads the full XML archive:

https://classic.clinicaltrials.gov/AllAPIXML.zip

---

## II. Processing Pipeline

### 1. Unzip Archive

- Unzip the `AllAPIXML` archive.
- This will create multiple folders named like:

```
NCTxxxxx
```

Each folder contains a single clinical trial XML file.

---

### 2. Clinical Trial Data Extraction

**Script:** `CT_01_extraction.py`  
**Input:** Root folder containing all `NCTxxxxx` XML folders  
**Output:** Single CSV file with clinical trial records  

Details:

- Iterates through all XML folders.
- Extracts predefined fields from each XML file.
- A single trial may contain:
  - Multiple diseases
  - Multiple interventions
- Output is written on a per disease – per intervention basis.

Example:

2 diseases × 3 interventions → 6 rows in output CSV

---

### 3. Metamapping (NLM 2019AB)

#### 3.1 Condition Metamapping

**Script:** `CT_02_metamap_condition.py`  
**Input:** CSV from Step 2 (with double quotes removed)  
**Output:** CSV with condition metamap columns filled  

Also generates:
- A dictionary caching:
  - Requested condition strings
  - Selected concepts
  - CUIs

---

#### 3.2 Intervention Metamapping

**Script:** `CT_03_metamap_intervention.py`  
**Input:** Output CSV from Step 3.1  
**Output:** CSV with intervention metamap columns filled  

Also generates:
- A dictionary caching:
  - Requested intervention strings
  - Selected concepts
  - CUIs

---

### 4. COVID Replacement Step [depreceated]

**Script:** `CT_04_COVID_replacement.py`  
**Input:** Output CSV from Step 3.2  
**Output:** CSV with COVID-19 replaced for both cause and effect parts  

---

### 5. Post-Metamap Deduplication

**Script:** `CT_05_deduplication.py`  
**Input:** Metamapped CSV from Step 3.2  
**Output:** Deduplicated CSV (reduced rows)

Purpose:

- Remove duplicates introduced by:
  - XML duplication
  - Metamap returning identical concepts
- Ensure column indices are correct (reassign if needed).
- Guarantees only unique Disease–Intervention pairs are loaded into the graph.

---

### 6. Final Aggregation (Prepare for Neo4j)

**Script:** `CT_06_aggregation.py`  
**Input:** Deduplicated CSV from Step 5  
**Output:** Extended CSV ready for Neo4j import  

Adds:

- Required Neo4j graph columns
- Evidence scores
- Dates (YYYYMMDD)
- Connective type
- Batch metadata:
  - `batch_generation` (e.g., 20200924)
  - `batch_version` (e.g., 0.4)

---

### 7. NGS Evidence Scoring

**Script:** `CT_07_ngs_scoring.py`  
**Input:** Aggregated CSV from Step 6  
**Output:** CSV with NGS Evidence scoring appended  

Scoring is based on concept presence in:

- Article Title
- Conclusion / Discussion section
- MeSH terms

---

### 8. Aggregate NGS Title Tagging

**Script:** `CT_08_title_tagging_agg.py`  
**Input:** Aggregated & scored CSV from Step 7  
**Output:** CSV with aggregated title tags appended  

---

### 9. Append MeSH Terms (CUI → MeSH Mapping)

**Script:** `CT_09_mesh_generation.py`  
**Input:** Aggregated, scored & tagged CSV from Step 8  
**Output:** CSV with MeSH terms appended  

Dependency:

- `UMLS_mesh_dict` (CUI → MeSH pickle file)
- Must be updated when a new UMLS release is available
- Current version: 2020AA

Purpose:

- Enable article indexing in the frontend (FE)

---

### 10. Append MeSH IDs and Terms

**Script:** `CT_10_mesh_generation.py`  
**Input:** Aggregated, scored & tagged CSV from Step 8  
**Output:** CSV with MeSH IDs and terms appended  

Purpose:

- Enable enhanced article indexing in the frontend (FE)

---

## Workflow Summary

```
XML Download
   ↓
Extraction
   ↓
Condition Metamap
   ↓
Intervention Metamap
   ↓
COVID Replacement
   ↓
Deduplication
   ↓
Aggregation (Neo4j Prep)
   ↓
NGS Scoring
   ↓
Title Tagging
   ↓
MeSH Generation

```
