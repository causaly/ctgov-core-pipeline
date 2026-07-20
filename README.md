# ClinicalTrials.gov Core Pipeline

Batch ETL pipeline that downloads ClinicalTrials.gov XML, maps conditions and interventions to UMLS concepts, produces evidence for the knowledge graph, and generates text files for search indexing.

The pipeline is orchestrated by `run_ct.sh` and runs on the production VM. For local development guidance, see [`AGENTS.md`](AGENTS.md).

## Data source

The pipeline downloads the full ClinicalTrials.gov XML archive:

```
https://classic.clinicaltrials.gov/AllAPIXML.zip
```

Each XML file represents one clinical trial. Extraction expands a trial into one row for every condition × intervention pair.

## Pipeline flow

```
XML → 01 extraction → 02 condition MetaMap → 03 intervention MetaMap
    → 05 deduplication → 06 evidence aggregation → 07 NGS scoring
    → 08 title tagging → 09 MeSH evidence output / 10 MeSH text metadata
    → 11 text-file generation
```

Step 04 (COVID replacement) is deprecated and is not run.

The principal outputs are:

- `{batch}_ctgov_main.tsv` — canonical evidence file for Neo4j and NGS
- `{batch}_ctgov_text.tar.gz` — text files for NGS indexing
- `{batch}_xml_dumps.zip` — source XML archive for the CT.gov embeddings pipeline

## Documentation

The detailed documents below are authoritative; keep them updated with pipeline changes.

| Document | Purpose |
|----------|---------|
| [`docs/overview.md`](docs/overview.md) | Pipeline, outputs, current versions, and documentation index |
| [`docs/pipeline-steps.md`](docs/pipeline-steps.md) | Inputs, outputs, and logic for each step |
| [`docs/running-the-pipeline.md`](docs/running-the-pipeline.md) | Production VM run procedure and troubleshooting |
| [`docs/umls-update.md`](docs/umls-update.md) | UMLS update procedure and QA |
| [`docs/outputs-and-downstream.md`](docs/outputs-and-downstream.md) | Evidence schema, GCS layout, and downstream consumers |
