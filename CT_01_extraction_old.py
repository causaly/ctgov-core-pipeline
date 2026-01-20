import csv
import os
import sys

from lxml import etree

writer = csv.writer(open(sys.argv[2], "w"), delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='')

header_row = ['filename', 'official_title', 'brief_title', 'condition', 'cond_mm_request', 'condition_concept',
              'condition_cui', 'condition_categories', 'condition_all_mm',
              'intervention_type', 'intervention_name', 'intervention_mm_request', 'intervention_concept',
              'intervention_cui', 'intervention_categories', 'intervention_all_mm', 'intervention_description',
              'overall_status', 'phase', 'study_type', 'eligibility_gender', 'eligibility_minimum_age',
              'eligibility_maximum_age', 'eligibility_healthy_volunteers', 'location_countries',
              'org_study_id', 'secondary_id', 'nct_id', 'lead_sponsor_agency', 'lead_sponsor_agency_class', 'source',
              'overall_status', 'study_design_intervention_model', 'study_design_primary_purpose',
              'study_design_masking', 'study_design_allocation', 'verification_date', 'study_first_posted',
              'last_update_posted', 'mesh_terms_condition', 'mesh_terms_intervention', 'primary_outcome',
              'secondary_outcome', 'enrollment', 'references']
writer.writerow(header_row)


data_path = sys.argv[1]

counter = 1
total_counter = 0
no_condition_and_no_intervention_counter = 0
unique_nct_ids = {}

# Go over all files in sorted fashion for reproducibility
for root, dirs, files in os.walk(data_path):
    dirs.sort()
    for file in sorted(files):

        total_counter += 1

        filename = os.path.join(root, file)
        if not filename.endswith(".xml"):
            continue
        print('FILENAME: {}'.format(filename))

        # THE XML FILES ARE READ IN USING etree.fromstring reader
        data = open(filename, 'rb')

        infile = data.read()
        art_tag = etree.fromstring(infile)

        #############################################################
        # INITIALIZE ALL FIELDS TO BE EXTRACTED
        org_study_id = '0'
        secondary_id = '0'
        nct_id = '0'
        lead_sponsor_agency = '0'           # eg NIH, Novartis
        lead_sponsor_agency_class = '0'
        overall_status = '0'                # TERMINATED, RECRUITING
        phase = '0'                         # Phase 1/2
        study_type = '0'
        source = '0'

        study_design_intervention_model = '0'
        study_design_primary_purpose = '0'
        study_design_masking = '0'
        study_design_allocation = '0'

        condition = []
        condition_cuis = []
        condition_cats = []

        intervention_type = []
        intervention_name = []
        intervention_cuis = []
        intervention_cats = []
        intervention_desc = []

        eligibility_gender = '0'
        eligibility_minimum_age = '0'
        eligibility_maximum_age = '0'
        eligibility_healthy_volunteers = '0'

        countries = []

        verification_date = '0'
        study_first_posted = '0'
        last_update_posted = '0'
        mesh_terms_condition = []
        mesh_terms_condition_cuis = []
        mesh_terms_condition_cats = []
        mesh_terms_intervention = []
        mesh_terms_intervention_cuis = []
        mesh_terms_intervention_cats = []

        primary_outcome = []
        secondary_outcome = []
        enrollment = '0'

        official_title = '0'
        brief_title = '0'

        trial_references = []
        # END VARIABLE INITIALIZING
        #############################################################

        # XML-BY-XML extract fields
        for main_tag in art_tag.getchildren():

            if main_tag.tag == 'overall_status' and main_tag.text is not None:
                overall_status = main_tag.text

            if main_tag.tag == 'phase' and main_tag.text is not None:
                phase = main_tag.text

            if main_tag.tag == 'study_type' and main_tag.text is not None:
                study_type = main_tag.text

            if main_tag.tag == 'sponsors':
                for sponsors_info in main_tag.getchildren():
                    if sponsors_info.tag == 'lead_sponsor':
                        for lead_sponsor in sponsors_info.getchildren():
                            if lead_sponsor.tag == 'agency':
                                lead_sponsor_agency = lead_sponsor.text
                            if lead_sponsor.tag == 'agency_class':
                                lead_sponsor_agency_class = lead_sponsor.text

            if main_tag.tag == 'id_info':
                for study_ids in main_tag.getchildren():
                    if study_ids.tag == 'org_study_id':
                        org_study_id = study_ids.text
                    if study_ids.tag == 'secondary_id':
                        secondary_id = study_ids.text
                    if study_ids.tag == 'nct_id':
                        nct_id = study_ids.text

            if main_tag.tag == 'source' and main_tag.text is not None:
                source = main_tag.text

            if main_tag.tag == 'study_design_info':
                for study_design in main_tag.getchildren():
                    if study_design.tag == 'intervention_model':
                        study_design_intervention_model = study_design.text
                    if study_design.tag == 'primary_purpose':
                        study_design_primary_purpose = study_design.text
                    if study_design.tag == 'masking':
                        study_design_masking = study_design.text
                    if study_design.tag == 'allocation':
                        study_design_allocation = study_design.text

            if main_tag.tag == 'condition' and main_tag.text is not None:
                condition.append(main_tag.text)

            if main_tag.tag == 'intervention':
                intervention_d = '0'
                for intervention in main_tag.getchildren():
                    if intervention.tag == 'intervention_type' and intervention.text is not None:
                        intervention_type.append(intervention.text)
                    if intervention.tag == 'intervention_name' and intervention.text is not None:
                        intervention_name.append(intervention.text)
                    if intervention.tag == 'description' and intervention.text is not None:
                        intervention_d = intervention.text.replace('\t', ' ').replace('\n', ' ')
                if intervention_d == '0':
                    intervention_desc.append('0')
                else:
                    intervention_desc.append(intervention_d)

            if main_tag.tag == 'eligibility':
                for eligibility in main_tag.getchildren():
                    if eligibility.tag == 'gender':
                        eligibility_gender = eligibility.text
                    if eligibility.tag == 'minimum_age':
                        eligibility_minimum_age = eligibility.text
                    if eligibility.tag == 'maximum_age':
                        eligibility_maximum_age = eligibility.text
                    if eligibility.tag == 'healthy_volunteers':
                        eligibility_healthy_volunteers = eligibility.text

            if main_tag.tag == 'location_countries':
                for location_countries in main_tag.getchildren():
                    if location_countries.tag == 'country':
                        countries.append(location_countries.text)

            if main_tag.tag == 'verification_date' and main_tag.text is not None:
                verification_date = main_tag.text

            if main_tag.tag == 'study_first_posted' and main_tag.text is not None:
                study_first_posted = main_tag.text

            if main_tag.tag == 'last_update_posted' and main_tag.text is not None:
                last_update_posted = main_tag.text

            if main_tag.tag == 'condition_browse':
                for condition_brow in main_tag.getchildren():
                    if condition_brow.tag == 'mesh_term':
                        mesh_terms_condition.append(condition_brow.text)

            if main_tag.tag == 'intervention_browse':
                for intervent_brow in main_tag.getchildren():
                    if intervent_brow.tag == 'mesh_term':
                        mesh_terms_intervention.append(intervent_brow.text)

            if main_tag.tag == 'primary_outcome':
                for prim_outcome in main_tag.getchildren():
                    if prim_outcome.tag == 'measure':
                        primary_outcome.append(prim_outcome.text)

            if main_tag.tag == 'secondary_outcome':
                for second_outcome in main_tag.getchildren():
                    if second_outcome.tag == 'measure':
                        secondary_outcome.append(second_outcome.text)

            if main_tag.tag == 'enrollment' and main_tag.text is not None:
                enrollment = main_tag.text

            if main_tag.tag == 'official_title' and main_tag.text is not None:
                official_title = main_tag.text

            if main_tag.tag == 'brief_title' and main_tag.text is not None:
                brief_title = main_tag.text

            if main_tag.tag in ['reference', 'results_reference']:
                for references in main_tag.getchildren():
                    if references.tag == 'PMID' and references.text is not None:
                        trial_references.append(references.text)

        if nct_id not in unique_nct_ids:
            unique_nct_ids[nct_id] = 1

        countries = '|'.join(countries)
        mesh_terms_condition = '|'.join(mesh_terms_condition)
        mesh_terms_intervention = '|'.join(mesh_terms_intervention)

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

                    row = [filename, official_title, brief_title, cond, '0', '0', '0', '0', '0',
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

                row = [filename, official_title, brief_title, cond, '0', '0', '0', '0', '0',
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

                row = [filename, official_title, brief_title, '0', '0', '0', '0', '0', '0',
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
print("Total readed input files: {}".format(total_counter))
print("Unique NCT ids: {}".format(len(unique_nct_ids)))
print("Articles with neither condition nor intervention: {}".format(no_condition_and_no_intervention_counter))
