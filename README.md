# This is a guide for obtaining, extracting and loading ClinicalTrials.gov records into Neo4j.
I. The data is obtained from clinicaltrials.gov
	- Current approach acquires all of the records as XML dump from  https://classic.clinicaltrials.gov/AllAPIXML.zip
II. Process:
	1. Unzip the ALLPublicXML archive to a location, it will create multiple internal folders (NCTxxxxx)
	2. Clinical Trial data extraction:
		Script: CT_01_extraction.py
		Input: the main folder with all NCT xmls
		Output: single csv file with Clinical Trial records
		- It iteratively goes through the folders and extracts predefined fields from xml files
		- A single clinical trial xml might have multiple diseases and multiple interventions
		- The script writes out the results on a per disease - per intervention basis (to form pairs)
			> So 2 diseases and 3 interventions in a single trial will yield 6 rows in the output csv
	3. Metamapping (NLM 2019AB)
		3.1 Condition metamapping
			Script: CT_02_metamap_condition.py
			Input: csv file from step 2 (with double quotes removed)
			Output: A new csv file with the same rows as the input csv and the condition metamap columns filled
				A dictionary that has cached the metamaped condition requested strings and the seleced concepts, cuis etc
		3.2 Intervention metamapping
			Script: CT_03_metamap_intervention.py
			Input: output csv file from step 3.1
			Output: A new csv file with the same rows as the input csv and the intervention metamap columns filled
				A dictionary that has cached the metamaped intervention requested strings and the seleced concepts, cuis etc
  4. COVID REPLACEMENT STEP
		 Script: CT_04_COVID_replacement.py
		 Input: output csv file from step 3.2
		 Output: A new csv file with the same rows and COVID-19 replaced for both cause & effect parts
	5. Postmetamap deduplication
		Script: CT_05_deduplication.py
		Input: Metamapped csv from step 4 (containing condition/intervention CUIs etc)
		Output: Same csv with less rows (deduplicated)
		- Once the metamap results are inserted into the csv, it needs to be deduplicated (duplicates might be present in the xml files + same concepts might have been returned by Metamap)
		- Make sure that column indices are as expected (re-assign indices otherwise)
		- The script makes sure that only unique Disease-Intervention pairs are to be loaded to the graph
	6. Final aggregation - prepare the csv for loading into Neo4j (adding more columns required by the graph and aggregating contents into them)
		Script: CT_06_aggregation.py
		Input: deduplicated metamapped csv from step 5
		Output: same csv with extended columns required for loading into Neo4j
		batch_generation: e.g 20200924
		batch_version: e.g 0.4
		- Takes the output csv from step 5, adds columns required by the Neo4j Graph and fills them correspondingly
		- Example of data added are Evidence scores, dates (YYYYMMDD), connective type etc.
	7. NGS SCoring - NGS Evidence scoring based on concept(s) presence in an Article Title, or Conclusion/Discussion section, or MeSH terms
	  Script: CT_07_ngs_scoring.py
		Input: Aggregated csv from step 6
		Output: same csv with NGS Evidence scoring appended
  8. AGGREGATE NGS TITLE TAGGING
		Script: CT_08_title_tagging_agg.py
		Input: Aggregated-scored csv from step 7
		Output: same csv with aggregated title tags appended
	9. Append mesh terms mapped from the extracted conditions and interventions cuis in order to allow article indexing in the FE
		Script: CT_09_mesh_generation.py
		Input: Aggregated-scored-tagged csv from step 8
		Output: Name for output csv file with the mesh terms appended
		UMLS_mesh_dict: Cui2mesh pickle file. NOTE pickle should be updated whenever a new umls release is availiable (Current version: 2020AA)
	10. Append mesh id and terms mapped from the extracted conditions and interventions cuis in order to allow article indexing in the FE
		Script: CT_10_mesh_generation.py
		Input: Aggregated-scored-tagged csv from step 8
		Output: Name for output csv file with the mesh terms appended
		UMLS_mesh_dict: Cui2mesh pickle file. NOTE pickle should be updated whenever a new umls release is availiable (Current version: 2020AA)
	11. Generate text files for ES
		Script: CT_11_text_generation.py
		Input: Outputs from step 10
		Output: text files for ES indexing
