#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import csv
import sys
from lxml import etree
import re

# TODO need to find a better way to deal with default encoding -- still does not run without excerpt below
#reload(sys)
#sys.setdefaultencoding('utf-8')

#writer = csv.writer(open('/Users/asaudabayev/corpus/05_ctgov/20200810/20200810_01_clinicaltrialsgov_xmlstage.csv', "w"), delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='')

writer = csv.writer(open(sys.argv[2], "w"), delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='')

header_row = ['filename', 'official_title', 'brief_title', 'condition', 'cond_mm_request', 'condition_concept', 'condition_cui', 'condition_categories', 'condition_all_mm',
              'intervention_type', 'intervention_name', 'intervention_mm_request', 'intervention_concept',
              'intervention_cui', 'intervention_categories', 'intervention_all_mm', 'intervention_description',
              'overall_status', 'phase', 'study_type', 'eligibility_gender', 'eligibility_minimum_age',
              'eligibility_maximum_age', 'eligibility_healthy_volunteers', 'location_countries',
              'org_study_id', 'secondary_id', 'nct_id', 'lead_sponsor_agency', 'lead_sponsor_agency_class',
              'collaborator', 'collaborator_class',
              'source',
              'study_design_intervention_model', 'study_design_primary_purpose',
              'study_design_masking', 'study_design_allocation', 'verification_date', 'study_first_posted',
              'last_update_posted', 'mesh_terms_condition', 'mesh_terms_intervention', 'primary_outcome', 'primary_outcome_description',
              'secondary_outcome', 'enrollment', 'references', 'synonyms', 'keywords',
              'start_date', 'start_type', 'completion_date', 'completion_type', 'primary_completion_date',
              'brief_summary', # 'detailed_description', 'arm_group', 'eligibility',
              ]
writer.writerow(header_row)


data_path = sys.argv[1]

subdirs = [x[0] for x in os.walk(data_path) if x[0] != data_path]

counter = 1
total_counter = 0
no_condition_and_no_intervention_counter = 0
unique_nct_ids = {}


def sanitise(input_str):
    input_str = input_str.strip()
    input_str = input_str.encode('ASCII', 'ignore').decode()
    input_str = input_str.replace('\n', ' ').replace('\t', ' ')
    input_str = re.sub(' +', ' ', input_str).strip()
    return input_str


def extract_synonyms_for_other_name(text):
    text = text.encode('ASCII', 'ignore').decode()
    text = text.strip()
    p1 = r'^([a-zA-Z\-0-9 ]+) \[([a-zA-Z0-9 ]+)\]$'
    p5 = r'^([a-zA-Z\-0-9 ]+) \(([a-zA-Z0-9 ]+)\)$'
    p2 = r'^([a-zA-Z ]+), ([a-zA-Z ]+)$'
    p3 = r'^([a-zA-Z ]+), ([a-zA-Z ]+), ([a-zA-Z ]+)$'
    p4 = r'^([a-zA-Z ]+), ([a-zA-Z ]+), ([a-zA-Z ]+), ([a-zA-Z ]+)$'
    # p1 = r'([^\[\]]+) \[([^\[\]]+)\]'
    m1 = re.search(p1, text)
    m5 = re.search(p5, text)
    m2 = re.search(p2, text)
    m3 = re.search(p3, text)
    m4 = re.search(p4, text)

    if m1:
        synonym1 = m1.group(1)
        synonym2 = m1.group(2)
        return '***'.join([synonym1, synonym2])
        ## return '==='.join([synonym1, synonym2])
    elif m5:
        synonym1 = m5.group(1)
        synonym2 = m5.group(2)
        return '***'.join([synonym1, synonym2])
        # return '==='.join([synonym1, synonym2])
    elif m2:
        synonym1 = m2.group(1)
        synonym2 = m2.group(2)
        return '***'.join([synonym1, synonym2])
    elif m3:
        synonym1 = m3.group(1)
        synonym2 = m3.group(2)
        synonym3 = m3.group(3)
        return '***'.join([synonym1, synonym2, synonym3])
    elif m4:
        synonym1 = m4.group(1)
        synonym2 = m4.group(2)
        synonym3 = m4.group(3)
        synonym4 = m4.group(4)
        return '***'.join([synonym1, synonym2, synonym3, synonym4])


    return text
    # return [text]


def extract_synonyms_for_intervention_name(text):
    # text = text.strip()
    p1 = r'^([a-zA-Z ]+) \[([a-zA-Z]+)\]$'
    p2 = r'^([a-zA-Z ]+) \(([a-zA-Z]+)\)$'
    m1 = re.search(p1, text)
    m2 = re.search(p2, text)

    if m1:
        synonym1 = m1.group(1)
        synonym2 = m1.group(2)
        return '==='.join([synonym1, synonym2])
    elif m2:
        synonym1 = m2.group(1)
        synonym2 = m2.group(2)
        return '==='.join([synonym1, synonym2])

    return text


# GO ON A SUBDIRECTORY-BY-SUBDIRECTORY BASIS
for subdir in subdirs:
    for file in os.listdir(subdir):

        total_counter += 1

        filename = subdir+'/'+file

        # THE XML FILES ARE READ IN USING etree.fromstring reader
        infile = open(filename).read()
        art_tag = etree.fromstring(infile)

        #############################################################
        # INITIALIZE ALL FIELDS TO BE EXTRACTED
        org_study_id = '0'
        secondary_id = '0'
        nct_id = '0'
        lead_sponsor_agency = '0'           # eg NIH, Novartis
        lead_sponsor_agency_class = '0'
        collaborator = '0'
        collaborator_class = '0'
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
        intervention_synonyms = []
        keywords = []

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
        primary_outcome_description = []
        secondary_outcome = []
        enrollment = '0'

        official_title = '0'
        brief_title = '0'

        start_date = '0'
        start_type = '0'
        completion_date = '0'
        completion_type = '0'
        primary_completion_date = '0'
        # intervention = '0'
        brief_summary = '0'
        # detailed_description = '0'
        # arm_group = '0'
        # eligibility = '0'

        trial_references = []
        # END VARIABLE INITIALIZING
        #############################################################

        # XML-BY-XML extract fields
        for main_tag in art_tag.getchildren():

            if main_tag.tag == 'overall_status' and main_tag.text != None:
                overall_status = main_tag.text

            if main_tag.tag == 'phase' and main_tag.text != None:
                phase = main_tag.text

            if main_tag.tag == 'study_type' and main_tag.text != None:
                study_type = main_tag.text

            if main_tag.tag == 'sponsors':
                for sponsors_info in main_tag.getchildren():
                    if sponsors_info.tag == 'lead_sponsor':
                        for lead_spons in sponsors_info.getchildren():
                            if lead_spons.tag == 'agency':
                                lead_sponsor_agency = lead_spons.text
                            if lead_spons.tag == 'agency_class':
                                lead_sponsor_agency_class = lead_spons.text
                    if sponsors_info.tag == 'collaborator':
                        for spons in sponsors_info.getchildren():
                            if spons.tag == 'agency':
                                collaborator = spons.text
                            if spons.tag == 'agency_class':
                                collaborator_class = spons.text

            if main_tag.tag == 'id_info':
                for study_ids in main_tag.getchildren():
                    if study_ids.tag == 'org_study_id':
                        org_study_id = study_ids.text
                    if study_ids.tag == 'secondary_id':
                        secondary_id = study_ids.text
                    if study_ids.tag == 'nct_id':
                        nct_id = study_ids.text

            if main_tag.tag == 'source' and main_tag.text != None:
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


            if main_tag.tag == 'condition' and main_tag.text != None:
                condition.append(main_tag.text)

            if main_tag.tag == 'intervention':
                intervention_d = '0'
                synonyms = []
                for intervention in main_tag.getchildren():
                    if intervention.tag == 'intervention_type' and intervention.text != None:
                        intervention_type.append(intervention.text)
                    if intervention.tag == 'intervention_name' and intervention.text != None:
                        intervention_name.append(intervention.text)
                        # name = extract_synonyms_for_intervention_name(intervention.text)
                        name = extract_synonyms_for_other_name(intervention.text)
                        # intervention_name.append(name)

                        b_names = name.split('===')
                        c_names = name.split('@@@')
                        if len(b_names) == 2:
                            synonyms.append('***'.join(b_names))
                            # synonyms.append('|||'.join(b_names))
                        elif len(c_names) > 1:
                            synonyms.append('***'.join(c_names))

                        # intervention_name += extract_synonyms(intervention.text)
                    if intervention.tag == 'description' and intervention.text != None:
                        intervention_d = intervention.text.replace('\t', ' ').replace('\n', ' ')
                    if intervention.tag == 'other_name' and intervention.text != None:
                        # synonyms += extract_synonyms_for_other_name(intervention.text)
                        synonyms.append(extract_synonyms_for_other_name(intervention.text))
                        # synonyms.append(intervention.text)
                if intervention_d == '0':
                    intervention_desc.append('0')
                else:
                    intervention_desc.append(intervention_d)

                if len(synonyms) > 0:
                    intervention_synonyms.append('***'.join(synonyms))
                    # intervention_synonyms.append('###'.join(synonyms))
                else:
                    intervention_synonyms.append('0')

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

            if main_tag.tag == 'keyword':
                pass
                # keywords.append(main_tag.text)

            if main_tag.tag == 'location_countries':
                for location_countries in main_tag.getchildren():
                    if location_countries.tag == 'country':
                        countries.append(location_countries.text)

            if main_tag.tag == 'verification_date' and main_tag.text != None:
                verification_date = main_tag.text

            if main_tag.tag == 'study_first_posted' and main_tag.text != None:
                study_first_posted = main_tag.text

            if main_tag.tag == 'last_update_posted' and main_tag.text != None:
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
                        primary_outcome_description.append(prim_outcome.text)
                    if prim_outcome.tag == 'description':
                        primary_outcome_description.append(prim_outcome.text)

            if main_tag.tag == 'secondary_outcome':
                for second_outcome in main_tag.getchildren():
                    if second_outcome.tag == 'measure':
                        secondary_outcome.append(second_outcome.text)

            if main_tag.tag == 'enrollment' and main_tag.text != None:
                enrollment = main_tag.text

            if main_tag.tag == 'official_title' and main_tag.text != None:
                # official_title = main_tag.text
                official_title = sanitise(main_tag.text)

            if main_tag.tag == 'brief_title' and main_tag.text != None:
                # brief_title = main_tag.text
                brief_title = sanitise(main_tag.text)

            if main_tag.tag == 'start_date' and main_tag.text != None:
                start_date = main_tag.text
                if main_tag.get('type'):
                    start_type = main_tag.get('type')

            if main_tag.tag == 'completion_date' and main_tag.text != None:
                completion_date = main_tag.text
                if main_tag.get('type'):
                    completion_type = main_tag.get('type')

            if main_tag.tag == 'primary_completion_date' and main_tag.text != None:
                primary_completion_date = main_tag.text

            # if main_tag.tag == 'intervention' and main_tag.text != None:
            #     intervention = sanitise(' '.join(main_tag.itertext()))

            if main_tag.tag == 'brief_summary' and main_tag.text != None:
                brief_summary = sanitise(' '.join(main_tag.itertext()))

            # if main_tag.tag == 'detailed_description' and main_tag.text != None:
            #     detailed_description = sanitise(' '.join(main_tag.itertext()))

            # if main_tag.tag == 'arm_group' and main_tag.text != None:
            #     arm_group = sanitise(' '.join(main_tag.itertext()))

            # if main_tag.tag == 'eligibility' and main_tag.text != None:
            #     eligibility = sanitise(' '.join(main_tag.itertext()))

            if main_tag.tag in ['reference', 'results_reference']:
                for references in main_tag.getchildren():
                    if references.tag == 'PMID' and references.text != None:
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
        final_intervention_synonyms = []
        for ind, item in enumerate(intervention_name):
            if item not in final_intervention_names:
                if ' + ' in item:
                    items = item.split(' + ')
                    for el in items:
                        final_intervention_names.append(el)
                        final_intervention_types.append(intervention_type[ind])
                        final_intervention_desc.append(intervention_desc[ind])
                        final_intervention_synonyms.append(intervention_synonyms[ind])
                elif ' or ' in item:
                    items = item.split(' or ')
                    for el in items:
                        final_intervention_names.append(el)
                        final_intervention_types.append(intervention_type[ind])
                        final_intervention_desc.append(intervention_desc[ind])
                        final_intervention_synonyms.append(intervention_synonyms[ind])
                else:
                    final_intervention_names.append(item)
                    final_intervention_types.append(intervention_type[ind])
                    final_intervention_desc.append(intervention_desc[ind])
                    final_intervention_synonyms.append(intervention_synonyms[ind])

        # SINGLE RECORD CAN CONTAIN MULTIPLE CONDITIONS AND INTERVENTIONS
        # WRITE THE RESULTS OUT PER CONDITION - PER INTERVENTION (to form rel pairs in the graph)
        # Include cases where we extract only condition(s) or only intervention(s)
        # Discard cases where we cannot extract neither condition(s) nor intervention(s)

        keywords = '###'.join(keywords)
        # keywords = '==='.join(keywords)
        primary_outcome_description = '###'.join(primary_outcome_description)
        # print(f'{nct_id}\t{overall_status}\t{start_date}\t{start_type}\t{completion_date}\t{completion_type}\t{primary_completion_date}')

        if len(final_conditions) > 0 and len(final_intervention_names) > 0:

            for cond in final_conditions:

                for ind, intervent in enumerate(final_intervention_names):

                    row = [filename, official_title, brief_title, cond, '0', '0', '0', '0', '0',
                           final_intervention_types[ind], final_intervention_names[ind], '0', '0', '0', '0', '0', final_intervention_desc[ind],
                           overall_status, phase,
                           study_type, eligibility_gender, eligibility_minimum_age, eligibility_maximum_age,
                           eligibility_healthy_volunteers, countries, org_study_id, secondary_id, nct_id, lead_sponsor_agency, lead_sponsor_agency_class,
                           collaborator, collaborator_class,
                           source, study_design_intervention_model,
                           study_design_primary_purpose, study_design_masking, study_design_allocation, verification_date,
                           study_first_posted, last_update_posted, mesh_terms_condition, mesh_terms_intervention, primary_outcome, primary_outcome_description,
                           secondary_outcome, enrollment, trial_references, final_intervention_synonyms[ind], keywords,
                           start_date, start_type, completion_date, completion_type, primary_completion_date,
                           brief_summary, # detailed_description, arm_group, eligibility
                           ]

                    row_clean = []
                    for x in row:
                        if isinstance(x,str):
                            row_clean.append(x.replace("\n","").replace("\r","").replace("\t"," ").replace('"',"'"))
                        #elif isinstance(x,unicode):
                        #    x = x.encode("utf-8")
                        #    row_clean.append(x.replace("\n","").replace("\r","").replace("\t"," ").replace('"',"'"))
                        elif isinstance(x,list):
                            xx_clean = []
                            for xx in x:
                                #if isinstance(xx,unicode):
                                #    xx = xx.encode("utf-8")
                                xx_clean.append(xx.replace("\n","").replace("\r","").replace("\t"," ").replace('"',"'"))
                            row_clean.append(xx_clean)

                    assert len(row_clean)==len(header_row),"Error on Condition+Intervention propagation!"
                    writer.writerow(row_clean)
                    counter += 1

        elif len(final_conditions) > 0 and len(final_intervention_names) == 0:

            for cond in final_conditions:

                row = [filename, official_title, brief_title, cond, '0', '0', '0', '0', '0',
                       '0', '0', '0', '0', '0', '0', '0', '0',overall_status, phase,
                       study_type, eligibility_gender, eligibility_minimum_age, eligibility_maximum_age,
                       eligibility_healthy_volunteers, countries, org_study_id, secondary_id, nct_id, lead_sponsor_agency, lead_sponsor_agency_class,
                       collaborator, collaborator_class,
                       source, study_design_intervention_model,
                       study_design_primary_purpose, study_design_masking, study_design_allocation, verification_date,
                       study_first_posted, last_update_posted, mesh_terms_condition, mesh_terms_intervention, primary_outcome, primary_outcome_description,
                       secondary_outcome, enrollment, trial_references, '0', '0',
                       start_date, start_type, completion_date, completion_type, primary_completion_date,
                       brief_summary, # detailed_description, arm_group, eligibility
                       ]

                row_clean = []
                for x in row:
                    if isinstance(x,str):
                        row_clean.append(x.replace("\n","").replace("\r","").replace("\t"," ").replace('"',"'"))
                    #elif isinstance(x,unicode):
                    #    x = x.encode("utf-8")
                    #    row_clean.append(x.replace("\n","").replace("\r","").replace("\t"," ").replace('"',"'"))
                    elif isinstance(x,list):
                        xx_clean = []
                        for xx in x:
                            #if isinstance(xx,unicode):
                            #    xx = xx.encode("utf-8")
                            xx_clean.append(xx.replace("\n","").replace("\r","").replace("\t"," ").replace('"',"'"))
                        row_clean.append(xx_clean)


                assert len(row_clean)==len(header_row),"Error on Condition propagation!"
                writer.writerow(row_clean)
                counter += 1

        elif len(final_conditions) == 0 and len(final_intervention_names) > 0:

            for ind, intervent in enumerate(final_intervention_names):

                row = [filename, official_title, brief_title, '0', '0', '0', '0', '0', '0',
                       final_intervention_types[ind], final_intervention_names[ind], '0', '0', '0', '0', '0', final_intervention_desc[ind],
                       overall_status, phase,
                       study_type, eligibility_gender, eligibility_minimum_age, eligibility_maximum_age,
                       eligibility_healthy_volunteers, countries, org_study_id, secondary_id, nct_id, lead_sponsor_agency, lead_sponsor_agency_class,
                       collaborator, collaborator_class,
                       source, study_design_intervention_model,
                       study_design_primary_purpose, study_design_masking, study_design_allocation, verification_date,
                       study_first_posted, last_update_posted, mesh_terms_condition, mesh_terms_intervention, primary_outcome, primary_outcome_description,
                       secondary_outcome, enrollment, trial_references, final_intervention_synonyms[ind], keywords,
                       start_date, start_type, completion_date, completion_type, primary_completion_date,
                       brief_summary, # detailed_description, arm_group, eligibility
                       ]

                row_clean = []
                for x in row:
                    if isinstance(x,str):
                        row_clean.append(x.replace("\n","").replace("\r","").replace("\t"," ").replace('"',"'"))
                    #elif isinstance(x,unicode):
                    #    x = x.encode("utf-8")
                    #    row_clean.append(x.replace("\n","").replace("\r","").replace("\t"," ").replace('"',"'"))
                    elif isinstance(x,list):
                        xx_clean = []
                        for xx in x:
                            #if isinstance(xx,unicode):
                            #    xx = xx.encode("utf-8")
                            xx_clean.append(xx.replace("\n","").replace("\r","").replace("\t"," ").replace('"',"'"))
                        row_clean.append(xx_clean)

                assert len(row_clean)==len(header_row),"Error on Interventions only propagation!"
                writer.writerow(row_clean)
                counter += 1

        else:
            no_condition_and_no_intervention_counter+=1



print(counter)
print(total_counter)
print(len(unique_nct_ids))
print("Articles with neither condition nor intervention: # " + str(no_condition_and_no_intervention_counter))
