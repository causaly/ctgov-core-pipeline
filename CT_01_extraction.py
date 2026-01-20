import csv
import json
import os
import sys

from lxml import etree as ET
from tqdm import tqdm
from utils.xml_parser import XMLParser

csv.field_size_limit(58000000)

if __name__ == "__main__":

    """
    Configuration variables
    """
    data_path = sys.argv[1]
    writer = csv.writer(open(sys.argv[2], "w"), delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='')

    header_row = ['filename', 'official_title', 'brief_title', 'condition', 'cond_mm_request', 'condition_concept',
                  'condition_cui', 'condition_categories', 'condition_all_mm',
                  'intervention_type', 'intervention_name', 'intervention_mm_request', 'intervention_concept',
                  'intervention_cui', 'intervention_categories', 'intervention_all_mm', 'intervention_description',
                  'overall_status', 'phase', 'study_type', 'eligibility_gender', 'eligibility_minimum_age',
                  'eligibility_maximum_age', 'eligibility_healthy_volunteers', 'location_countries',
                  'org_study_id', 'secondary_id', 'nct_id', 'lead_sponsor_agency', 'lead_sponsor_agency_class',
                  'source',
                  'overall_status', 'study_design_intervention_model', 'study_design_primary_purpose',
                  'study_design_masking', 'study_design_allocation', 'verification_date', 'study_first_posted',
                  'last_update_posted', 'mesh_terms_condition', 'mesh_terms_intervention', 'primary_outcome',
                  'secondary_outcome', 'enrollment', 'references']
    writer.writerow(header_row)

    counter = 1
    total_counter = 0
    no_condition_and_no_intervention_counter = 0
    unique_nct_ids = {}

    RULES_FILE_PATH = "config" + os.sep + "rules.json"
    with open(RULES_FILE_PATH, "r") as f:
        rules = json.load(f)

    input_xml_paths = []
    for path, dirs, files in os.walk(data_path):
        dirs.sort()
        for file in sorted(files):
            if file.endswith(".xml"):
                input_xml_paths.append(os.path.join(path, file))

    parser = ET.XMLParser(remove_comments=True, huge_tree=True)
    xml_parser_obj = XMLParser(rules)
    for xml_path in tqdm(input_xml_paths, desc="Files Processed: "):
        total_counter += 1
        xml = ET.parse(xml_path, parser=parser)
        parsed_output = xml_parser_obj.start_parsing(xml)

        # INITIALIZE ALL FIELDS TO BE EXTRACTED
        org_study_id = parsed_output["org_study_id"]
        secondary_id = parsed_output["secondary_id"]
        nct_id = parsed_output["nct_id"]
        assert len(parsed_output["sponsors"]) < 2, "Lead sponsors > 1"
        if len(parsed_output["sponsors"]) == 1:
            lead_sponsor_agency = parsed_output["sponsors"][0]["sponsor_name"]  # eg NIH, Novartis
            lead_sponsor_agency_class = parsed_output["sponsors"][0]["sponsor_type"]
        else:
            lead_sponsor_agency = '0'
            lead_sponsor_agency_class = '0'
        overall_status = parsed_output["overall_status"]  # TERMINATED, RECRUITING
        if isinstance(parsed_output["study_phases"], list):
            phase = "/".join(parsed_output["study_phases"])  # Phase 1/2
        else:
            phase = parsed_output["study_phases"].replace("Not Applicable", "N/A")
        study_type = parsed_output["study_type"]
        if len(parsed_output["source"]) == 1:
            source = parsed_output["source"][0]["source_name"]
        else:
            source = '0'

        study_design_intervention_model = parsed_output["study_design_intervention_model"]
        study_design_primary_purpose = parsed_output["study_design_primary_purpose"]
        study_design_masking = parsed_output["study_design_masking"]
        study_design_allocation = parsed_output["study_design_allocation"]

        condition = []
        condition_cuis = []
        condition_cats = []

        intervention_type = []
        intervention_name = []
        intervention_cuis = []
        intervention_cats = []
        intervention_desc = []

        if "eligibility_criteria" in parsed_output and len(parsed_output["eligibility_criteria"]) == 1:
            eligibility_gender = parsed_output["eligibility_criteria"][0]["eligibility_gender"]
            eligibility_minimum_age = parsed_output["eligibility_criteria"][0]["eligibility_min_age"]
            eligibility_maximum_age = parsed_output["eligibility_criteria"][0]["eligibility_max_age"]
            eligibility_healthy_volunteers = parsed_output["eligibility_criteria"][0]["eligibility_healthy_volunteers"]
        else:
            eligibility_gender = '0'
            eligibility_minimum_age = '0'
            eligibility_maximum_age = '0'
            eligibility_healthy_volunteers = '0'

        countries = ""
        if isinstance(parsed_output["location_countries"], list):
            countries = "|".join(sorted(list(set(parsed_output["location_countries"]))))
        elif isinstance(parsed_output["location_countries"], str):
            if (parsed_output["location_countries"] != '0' and parsed_output["location_countries"] != 0 and
                    parsed_output["location_countries"] is not None and
                    len(parsed_output["location_countries"].strip()) > 0):
                countries = parsed_output["location_countries"].strip()

        verification_date = parsed_output["status_verification_date"]
        study_first_posted = parsed_output["study_first_post_date"]
        last_update_posted = parsed_output["study_last_update_post_date"]
        mesh_terms_condition = []
        mesh_terms_condition_cuis = []
        mesh_terms_condition_cats = []
        mesh_terms_intervention = []
        mesh_terms_intervention_cuis = []
        mesh_terms_intervention_cats = []

        primary_outcome = []
        secondary_outcome = []
        enrollment = parsed_output["study_enrollment_count"]

        official_title = parsed_output["official_title"]
        brief_title = parsed_output["brief_title"]

        trial_references = []
        for ref in parsed_output["Reference_articles"]:
            trial_references.append(ref["reference_pmid"])

        # END VARIABLE INITIALIZING
        #############################################################

        if isinstance(parsed_output["conditions"], str):
            condition.append(parsed_output["conditions"])
        elif isinstance(parsed_output["conditions"], list):
            condition.extend(parsed_output["conditions"])
        else:
            print("Condition format error neither string nor list")
            sys.exit()

        for inter in parsed_output["interventions"]:
            intervention_name.append(inter["intervention_name"])
            intervention_type.append(inter["intervention_type"])
            intervention_d = inter["intervention_description"].replace('\t', ' ').replace('\n', ' ')
            if (intervention_d is not None and intervention_d != '0' and intervention_d != 0
                    and len(intervention_d.strip()) > 0):
                intervention_desc.append(intervention_d)
            else:
                intervention_desc.append('0')

        for tag in ["condition_mesh_terms", "relevant_condition_mesh_terms"]:
            if (parsed_output[tag] != '0' and parsed_output[tag] != 0 and
                    parsed_output[tag] is not None):

                if isinstance(parsed_output[tag], str) and len(
                        parsed_output[tag].strip()) > 0:
                    mesh_terms_condition.append(parsed_output[tag])
                elif isinstance(parsed_output[tag], list):
                    mesh_terms_condition.extend(parsed_output[tag])

        for tag in ["intervention_mesh_terms", "relevant_intervention_mesh_terms"]:
            if (parsed_output[tag] != '0' and parsed_output[tag] != 0 and
                    parsed_output[tag] is not None):

                if isinstance(parsed_output[tag], str) and len(
                        parsed_output[tag].strip()) > 0:
                    mesh_terms_intervention.append(parsed_output[tag])
                elif isinstance(parsed_output[tag], list):
                    mesh_terms_intervention.extend(parsed_output[tag])

        for pr_outcome in parsed_output["primary_outcomes"]:
            primary_outcome.append(pr_outcome["outcome_measure"])

        for sec_outcome in parsed_output["secondary_outcomes"]:
            secondary_outcome.append(sec_outcome["outcome_measure"])

        if nct_id not in unique_nct_ids:
            unique_nct_ids[nct_id] = 1

        mesh_terms_condition = '|'.join(sorted(list(set(mesh_terms_condition))))
        mesh_terms_intervention = '|'.join(sorted(list(set(mesh_terms_intervention))))

        if len(trial_references) == 0:
            trial_references = '0'
        else:
            trial_references = '|'.join(trial_references)

        # deduplicate interventions and conditions
        final_conditions = []
        for item in condition:
            if item not in final_conditions:
                final_conditions.append(item)

        final_intervention_names = []
        final_intervention_types = []
        final_intervention_desc = []
        for ind, item in enumerate(intervention_name):
            if item not in final_intervention_names:
                if ' + ' in item:
                    items = item.split(' + ')
                    for el in items:
                        final_intervention_names.append(el)
                        final_intervention_types.append(intervention_type[ind])
                        final_intervention_desc.append(intervention_desc[ind])
                elif ' or ' in item:
                    items = item.split(' or ')
                    for el in items:
                        final_intervention_names.append(el)
                        final_intervention_types.append(intervention_type[ind])
                        final_intervention_desc.append(intervention_desc[ind])
                else:
                    final_intervention_names.append(item)
                    final_intervention_types.append(intervention_type[ind])
                    final_intervention_desc.append(intervention_desc[ind])

        # SINGLE RECORD CAN CONTAIN MULTIPLE CONDITIONS AND INTERVENTIONS
        # WRITE THE RESULTS OUT PER CONDITION - PER INTERVENTION (to form rel pairs in the graph)
        # Include cases where we extract only condition(s) or only intervention(s)
        # Discard cases where we cannot extract neither condition(s) nor intervention(s)

        if len(final_conditions) > 0 and len(final_intervention_names) > 0:

            for cond in final_conditions:

                for ind, intervent in enumerate(final_intervention_names):

                    row = [xml_path, official_title, brief_title, cond, '0', '0', '0', '0', '0',
                           final_intervention_types[ind], final_intervention_names[ind], '0', '0', '0', '0', '0',
                           final_intervention_desc[ind],
                           overall_status, phase,
                           study_type, eligibility_gender, eligibility_minimum_age, eligibility_maximum_age,
                           eligibility_healthy_volunteers, countries, org_study_id, secondary_id, nct_id,
                           lead_sponsor_agency,
                           lead_sponsor_agency_class, source, overall_status, study_design_intervention_model,
                           study_design_primary_purpose, study_design_masking, study_design_allocation,
                           verification_date, study_first_posted, last_update_posted, mesh_terms_condition,
                           mesh_terms_intervention,
                           primary_outcome, secondary_outcome, enrollment, trial_references]

                    row_clean = []
                    for x in row:
                        if isinstance(x, str):
                            row_clean.append(x.replace("\n", "").replace("\r", "").replace("\t", " ").replace('"', "'"))
                        elif isinstance(x, list):
                            xx_clean = []
                            for xx in x:
                                xx_clean.append(xx.replace("\n", "").replace("\r", "").replace("\t", " ").
                                                replace('"', "'"))
                            row_clean.append(xx_clean)

                    assert len(row_clean) == len(header_row), "Error on Condition+Intervention propagation!"
                    writer.writerow(row_clean)
                    counter += 1

        elif len(final_conditions) > 0 and len(final_intervention_names) == 0:

            for cond in final_conditions:

                row = [xml_path, official_title, brief_title, cond, '0', '0', '0', '0', '0',
                       '0', '0', '0', '0', '0', '0', '0', '0', overall_status, phase,
                       study_type, eligibility_gender, eligibility_minimum_age, eligibility_maximum_age,
                       eligibility_healthy_volunteers, countries, org_study_id, secondary_id, nct_id,
                       lead_sponsor_agency,
                       lead_sponsor_agency_class, source, overall_status, study_design_intervention_model,
                       study_design_primary_purpose, study_design_masking, study_design_allocation, verification_date,
                       study_first_posted, last_update_posted, mesh_terms_condition, mesh_terms_intervention,
                       primary_outcome,
                       secondary_outcome, enrollment, trial_references]

                row_clean = []
                for x in row:
                    if isinstance(x, str):
                        row_clean.append(x.replace("\n", "").replace("\r", "").replace("\t", " ").replace('"', "'"))
                    elif isinstance(x, list):
                        xx_clean = []
                        for xx in x:
                            xx_clean.append(xx.replace("\n", "").replace("\r", "").replace("\t", " ").replace('"', "'"))
                        row_clean.append(xx_clean)

                assert len(row_clean) == len(header_row), "Error on Condition propagation!"
                writer.writerow(row_clean)
                counter += 1

        elif len(final_conditions) == 0 and len(final_intervention_names) > 0:

            for ind, intervent in enumerate(final_intervention_names):

                row = [xml_path, official_title, brief_title, '0', '0', '0', '0', '0', '0',
                       final_intervention_types[ind], final_intervention_names[ind], '0', '0', '0', '0', '0',
                       final_intervention_desc[ind], overall_status, phase,
                       study_type, eligibility_gender, eligibility_minimum_age, eligibility_maximum_age,
                       eligibility_healthy_volunteers, countries, org_study_id, secondary_id, nct_id,
                       lead_sponsor_agency,
                       lead_sponsor_agency_class, source, overall_status, study_design_intervention_model,
                       study_design_primary_purpose, study_design_masking, study_design_allocation, verification_date,
                       study_first_posted, last_update_posted, mesh_terms_condition, mesh_terms_intervention,
                       primary_outcome, secondary_outcome, enrollment, trial_references]

                row_clean = []
                for x in row:
                    if isinstance(x, str):
                        row_clean.append(x.replace("\n", "").replace("\r", "").replace("\t", " ").replace('"', "'"))
                    elif isinstance(x, list):
                        xx_clean = []
                        for xx in x:
                            xx_clean.append(xx.replace("\n", "").replace("\r", "").replace("\t", " ").replace('"', "'"))
                        row_clean.append(xx_clean)

                assert len(row_clean) == len(header_row), "Error on Interventions only propagation!"
                writer.writerow(row_clean)
                counter += 1

        else:
            no_condition_and_no_intervention_counter += 1

    print("Total output rows (included header row): {}".format(counter))
    print("Total read input files: {}".format(total_counter))
    print("Unique NCT ids: {}".format(len(unique_nct_ids)))
    print("Articles with neither condition nor intervention: {}".format(no_condition_and_no_intervention_counter))
