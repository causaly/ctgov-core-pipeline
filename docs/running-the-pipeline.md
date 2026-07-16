# Running the Pipeline

Operational runbook for a standard ClinicalTrials.gov batch release on the production VM.

**Confluence reference:** [Run pipeline (step by step)](https://causaly.atlassian.net/wiki/spaces/DaST/pages/2710372353/Run+pipeline+step+by+step)

---

## Prerequisites

The pipeline runs on a dedicated GCP VM with locally installed MetaMap and UMLS resources. These are **not** in the git repo — they must exist on the VM before running.

### VM and tooling

| Requirement | Location / detail |
|-------------|-------------------|
| **VM** | `prd-pipeline-ct-gov` (`us-east1-b`, project `causaly-prd-pipeline`, IP `10.51.1.23`) |
| **SSH** | Via `gcp-util-bastion-prd` (ProxyJump) |
| **Repo** | `/home/m.kyriakakis/ctgov-core-pipeline` (or equivalent checkout) |
| **MetaMap** | `/tools/metamap_2020/public_mm/bin/metamap` |
| **MetaMap UMLS** | `-Z 2023AB` |
| **MetaMap custom vocab** | `-V custom2025AB` |
| **UMLS scoring pickles** | `/tools/metathesaurus_files/2025AB_data/` (`atoms`, `parents`, `children`, `cui_to_cat` — `.pkl2` for Python 2.7) |
| **CUI→MeSH pickle** | `cui2mesh_2025AB_merged_2023AB.pkl` (repo root) |
| **Semantic type config** | `umls_statex.xlsx` (repo root) |
| **CUI blacklist** | `utils/Universal_statex_blacklist.xlsx` |
| **GCS credentials** | `gcloud_service_account.json` (repo root, gitignored) |
| **Python** | Python 3 (steps 01, 09–11) + Python 2.7 (steps 02–08) |
| **Spacy model** | `en_core_web_sm` (MetaMap preprocessing) |

### GCP console links

- [VM instance](https://console.cloud.google.com/compute/instancesDetail/zones/us-east1-b/instances/prd-pipeline-ct-gov?project=causaly-prd-pipeline)
- [Compute instances list](https://console.cloud.google.com/compute/instances?project=causaly-prd-pipeline)

---

## Standard batch run

### 1. Start the VM

Start `prd-pipeline-ct-gov` from the [GCP console](https://console.cloud.google.com/compute/instances?project=causaly-prd-pipeline) if it is stopped.

### 2. SSH into the VM

```bash
ssh -J gcp-util-bastion-prd m.kyriakakis@10.51.1.23
```

### 3. Navigate to the repo

```bash
cd /home/m.kyriakakis/ctgov-core-pipeline
```

### 4. Start a screen session

The full pipeline run takes many hours. Use `screen` to survive SSH disconnects:

```bash
screen -S CT
```

### 5. Ensure execute permissions

```bash
chmod +x run_ct.sh
```

### 6. Run the pipeline

```bash
./run_ct.sh YYYYMMDD
```

Where `YYYYMMDD` is the **batch_gen** value (e.g. `20260517`). Must be exactly 8 digits.

**What `run_ct.sh` does:**
1. Cleans previous run artifacts from disk
2. Downloads and unzips `AllAPIXML.zip`
3. Runs steps 01–11 sequentially (see [pipeline-steps.md](pipeline-steps.md))
4. Starts MetaMap servers (`skrmedpostctl` on port 1795, `wsdserverctl` on port 5554) before steps 02 and 03 if not already running
5. Archives `txt-files/` as `{batch}_ctgov_text.tar.gz`
6. Uploads all outputs to `gs://prd-ngs-ctgov/{batch}/`
7. Generates `{batch}_stats.txt`

### 7. Update the release stats page

After the pipeline finishes, update the [CTgov run log](https://causaly.atlassian.net/wiki/spaces/DaST/pages/409698422) Confluence page using values from `{batch}_stats.txt` in the repo root. See [outputs-and-downstream.md](outputs-and-downstream.md) for column meanings and the update procedure.

### 8. Notify the team

Post in `context-release-channel` that data is ready, pointing to the GCS path:

```
gs://prd-ngs-ctgov/{batch}/
```

---

## Logs and monitoring

| Artifact | Location |
|----------|----------|
| Per-step logs | `{batch}_logs/01.log` … `11.log` |
| MetaMap chunk logs | `metamap_conditions_logs/`, `metamap_interventions_logs/` |
| Intermediate TSVs | `Intermediate_steps/CT_{batch}_{step}.tsv` |
| Stats file | `{batch}_stats.txt` |

All logs and intermediate files are uploaded to GCS alongside the final outputs.

---

## Troubleshooting

### MetaMap servers not responding

`run_ct.sh` checks ports 1795 and 5554 before steps 02 and 03. If servers fail to start:

```bash
bash /tools/metamap_2020/public_mm/bin/skrmedpostctl start
# wait ~30s
bash /tools/metamap_2020/public_mm/bin/wsdserverctl start
# wait ~120s
```

Verify with `netstat -tulpn | grep -E '1795|5554'`.

### Step 07 (NGS scoring) stalls

Usually caused by missing CUIs in the `cui_to_cat` dictionary. Run [`misc/find_missing_cui2cat.py`](../misc/find_missing_cui2cat.py) against the step 03 output and patch `missing_cuis_dict` in [`misc/cui_to_cat_dict_build.py`](../misc/cui_to_cat_dict_build.py). See [umls-update.md](umls-update.md).

### GCS upload fails

Verify the service account key exists and is valid:

```bash
gcloud auth activate-service-account --key-file $PWD/gcloud_service_account.json
gsutil ls gs://prd-ngs-ctgov/
```

### Resuming a failed run

`run_ct.sh` does not support resume-from-step. If a step fails:
1. Fix the issue
2. Re-run `./run_ct.sh YYYYMMDD` from the beginning (cleanup at the start wipes intermediate state)

To debug a single step manually, invoke the script directly with the correct input/output paths (see [pipeline-steps.md](pipeline-steps.md)).

### Disk space

The full XML dump + intermediate TSVs + metamap caches can consume significant disk. `run_ct.sh` cleans previous run artifacts at the start, but monitor disk usage on long runs.
