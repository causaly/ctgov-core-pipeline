#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import csv
import sys
import hashlib
import re
import ast
import datetime as dt
import dateutil.parser as dp

# TODO need to find a better way to deal with default encoding -- still does not run without excerpt below
reload(sys)
sys.setdefaultencoding('utf-8')

csv.field_size_limit(58000000)

month_dict = {
    'january': '01',
    'february': '02',
    'march': '03',
    'april': '04',
    'may': '05',
    'june': '06',
    'july': '07',
    'august': '08',
    'september': '09',
    'october': '10',
    'november': '11',
    'december': '12'
}

src_filename_ind = 0
src_official_title_ind = 1
src_brief_title_ind = 2
src_condition_ind = 3
src_cond_mm_request_ind = 4
src_condition_concept_ind = 5
src_condition_cui_ind = 6
src_condition_categories_ind = 7
src_condition_all_mm_ind = 8
src_intervention_type_ind = 9
src_intervention_name_ind = 10
src_intervention_mm_request_ind = 11
src_intervention_concept_ind = 12
src_intervention_cui_ind = 13
src_intervention_categories_ind = 14
src_intervention_all_mm_ind = 15
src_intervention_description_ind = 16
src_overall_status_ind_1 = 17
src_phase_ind = 18
src_study_type_ind = 19
src_eligibility_gender_ind = 20
src_eligibility_minimum_age_ind = 21
src_eligibility_maximum_age_ind = 22
src_eligibility_healthy_volunteers_ind = 23
src_location_countries_ind = 24
src_org_study_id_ind = 25
src_secondary_id_ind = 26
src_nct_id_ind = 27
src_lead_sponsor_agency_ind = 28
src_lead_sponsor_agency_class_ind = 29
src_source_ind = 30
src_overall_status_ind_2 = 31
src_study_design_intervention_model_ind = 32
src_study_design_primary_purpose_ind = 33
src_study_design_masking_ind = 34
src_study_design_allocation_ind = 35
src_verification_date_ind = 36
src_study_first_posted_ind = 37
src_last_update_posted_ind = 38
src_mesh_terms_condition_ind = 39
src_mesh_terms_intervention_ind = 40
src_primary_outcome_ind = 41
src_secondary_outcome_ind = 42
src_enrollment_ind = 43
src_references_ind = 44


#filename = '/Users/asaudabayev/corpus/05_ctgov/20200810/deduped_covid_replaced_20200810_01_clinicaltrialsgov_xmlstage_condition+intervention.csv'
filename = sys.argv[1]

#writer = csv.writer(open('/Users/asaudabayev/corpus/05_ctgov/20200810/toload_deduped_covid_replaced_20200810_01_clinicaltrialsgov_xmlstage_condition+intervention.csv', "w"), delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='')
writer = csv.writer(open(sys.argv[2],"w"), delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='')
#writer_test = csv.writer(open('/Users/asaudabayev/corpus/05_ctgov/20200810/test_deduped_covid_replaced_20200810_01_clinicaltrialsgov_xmlstage_condition+intervention.csv', "w"), delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='')

header_row = ['filename', 'sentence_n', 'sentence_f', 'content_raw', 'is Causal', 'topic', 'connective',
              'connective_case', 'connective_type', 'connective_negation', 'connective_aux', 'connective_tempus',
              'clause', 'clause_neg', 'clause_aux', 'db_remark', 'cause_phrase', 'cause_keyword',
              'cause_keyword_display', 'cause_event', 'cause_keyword_NMOD', 'cause_switch', 'cause_concept',
              'Cause Concept Conf', 'effect_phrase', 'effect_keyword', 'effect_keyword_display', 'effect_event',
              'effect_keyword_NMOD', 'effect_switch', 'effect_concept', 'Effect Concept Conf', 'chaining', 'duplicate',
              'Cause Clause Type', 'effect_advcl', 'Extract Cause Tag', 'RES_ROOT_NMOD_BY', 'ACL SUCH AS',
              'tuple_order', 'indirect_causality', 'issn', 'journal_title', 'publisher', 'pmid', 'pmc', 'pii',
              'publisher_id', 'doi', 'pub_date', 'article_title', 'article_authors', 'article_keywords',
              'old_article_type', 'article_citation_number', 'article_category', 'article_access', 'text_type',
              'article_section_compartment', 'article_section_original', 'article_section_bucket',
              'article_heading_cat', 'article_type_tag', 'total_score_conf', 'total_score_strength_norm', 'relevance',
              'hypothetical_flag', 'pub_date_year', 'journal_sjr', 'journal_sjr_quartile', 'journal_hindex',
              'journal_categories', 'article_title_reduced', 'article_hashcode', 'source_hashcode', 'cause_category',
              'cause_concept_cui', 'cause_concept_matched', 'effect_category', 'effect_concept_cui',
              'effect_concept_matched', 'cause_concept_option', 'cause_category_option', 'cause_concept_option_score',
              'cause_concept_option_cui', 'cause_event_concept_option', 'cause_category_event_option',
              'cause_event_concept_option_score', 'cause_event_concept_option_cui', 'effect_concept_option',
              'effect_category_option', 'effect_concept_option_score', 'effect_concept_option_cui',
              'effect_event_concept_option', 'effect_category_event_option', 'effect_event_concept_option_score',
              'effect_event_concept_option_cui', 'cause_concept_secondary', 'cause_concept_secondary_conf',
              'cause_category_secondary', 'cause_concept_secondary_cui', 'effect_concept_secondary',
              'effect_concept_secondary_conf', 'effect_category_secondary', 'effect_concept_secondary_cui',
              'last_update_op', 'article_pt', 'article_mesh_terms', 'article_mesh_qualifiers', 'mesh_source',
              'article_uuid', 'primary_id', 'secondary_id', 'tertiary_id', 'data_source', 'article_type',
              'batch_generation', 'parse_version', 'sem_type', 'type_changes', 'assoc_switch']

writer.writerow(header_row)
#writer_test.writerow(header_row)

counter = 0

dates_wrong = 0

seen_source_hashes = {}

with open(filename, 'r') as my_file:
    reader = csv.reader(my_file, delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='')

    for idx, row in enumerate(reader):

        if idx == 0:
            continue

        out_filename = row[src_filename_ind]  # 1
        sentence_n = '0'                      # 2
        sentence_f = '0'                      # 3

        # COMBINE THE CONTENT RAW             # 4
        # a) Prim outcome
        prim_outcome_raw = row[src_primary_outcome_ind].replace('[', '').replace(']', '').split(', ')
        prim_outcome = filter(None, prim_outcome_raw)
        if len(prim_outcome) == 0:
            out_content_raw = ''
        elif len('|'.join(prim_outcome)) > 200:
            prim_outcome = '|'.join(prim_outcome).replace('\'', '')
            out_content_raw = '<b>Primary Outcome: </b>' + prim_outcome
            out_content_raw = out_content_raw[:195] + '(...)' + '<br/>'
        else:
            prim_outcome = '|'.join(prim_outcome).replace('\'', '')
            out_content_raw = '<b>Primary Outcome: </b>' + prim_outcome + '<br/>'
        # b) Study Type
        if row[src_study_type_ind] != '0' and row[src_study_type_ind] != '0' and row[src_study_type_ind] != None and row[src_study_type_ind] != '[]':
            out_content_raw += '<b>Study Type: </b>' + row[src_phase_ind] + ', ' + row[src_study_type_ind] + '<br/>'
        # c) Study Design
        study_design = ''
        if row[src_study_design_intervention_model_ind] != '0':
            study_design += row[src_study_design_intervention_model_ind] + ', '
        if row[src_study_design_primary_purpose_ind] != '0' and len(study_design) < 200:
            study_design += row[src_study_design_primary_purpose_ind] + ', '
        if row[src_study_design_masking_ind] != '0' and len(study_design) < 200:
            study_design += row[src_study_design_masking_ind] + ', '
        if row[src_study_design_allocation_ind] != '0' and len(study_design) < 200:
            study_design += row[src_study_design_allocation_ind] + ', '
        if row[src_enrollment_ind] != '0' and row[src_enrollment_ind] != 0 and len(study_design) < 200:
            study_design += row[src_enrollment_ind] + ' enrolled'
        study_design = study_design.strip(', ')
        out_content_raw += '<b>Study Design: </b>' + study_design + '<br/>'
        # d) Status
        if row[src_overall_status_ind_1] != '0' and row[src_overall_status_ind_1] != '' and row[src_overall_status_ind_1] != None:
            out_content_raw += '<b>Status: </b>' + row[src_overall_status_ind_1]
        # COMBINE THE CONTENT RAW             # 4

        out_is_causal = '1'                   # 5

        out_topic = '0'                       # 6
        out_connective = '0'                  # 7
        out_connective_case = '0'             # 8
        out_connective_type = 'OBSERVATION'   # 9
        out_connective_negation = '0'         # 10
        out_connective_aux = '0'              # 11
        out_connective_tempus = '0'           # 12
        out_clause = '0'                      # 13
        out_clause_neg = '0'                  # 14
        out_clause_aux = '0'                  # 15
        out_db_remark = '0'                   # 16
        out_cause_phrase = '0'                # 17

        out_cause_keyword = row[src_intervention_name_ind]  # 18
        out_cause_keyword_display = row[src_intervention_name_ind].lower() # 19

        out_cause_event = '0'                 # 20
        out_cause_keyword_NMOD = '0'          # 21
        out_cause_switch = '0'                # 22

        out_cause_concept = row[src_intervention_concept_ind]   # 23

        out_cause_concept_conf = '0'          # 24
        out_effect_phrase = '0'               # 25

        out_effect_keyword = row[src_condition_ind] # 26
        out_effect_keyword_display = row[src_condition_ind].lower() # 27

        out_effect_event = '0'                # 28
        out_effect_keyword_NMOD = '0'         # 29
        out_effect_switch = '0'               # 30

        out_effect_concept = row[src_condition_concept_ind] # 31

        out_effect_concept_conf = '0'         # 32
        out_chaining = '0'                    # 33
        out_duplicate = '0'                   # 34
        out_cause_clause_type = '0'           # 35
        out_effect_advcl = '0'                # 36
        out_extract_cause_tag = '0'           # 37
        out_RES_ROOT_NMOD_BY = '0'            # 38
        out_ACL_SUCH_AS = '0'                 # 39
        out_tuple_order = '0'                 # 40
        out_indirect_causality = '0'          # 41

        # DEAL WITH ISSN                      # 42
        if row[src_lead_sponsor_agency_ind] != '0' and row[src_lead_sponsor_agency_ind] != '' and row[src_lead_sponsor_agency_ind] != None:
            lead_sponsor = row[src_lead_sponsor_agency_ind].lower()
            lead_sponsor_reduced = re.sub('[^a-z]+', '', lead_sponsor)
            lead_sponsor_hash = hashlib.sha256(lead_sponsor_reduced).hexdigest()
        else:
            lead_sponsor_hash = '0'
        out_issn = lead_sponsor_hash
        # DEAL WITH ISSN                      # 42

        out_journal_title = row[src_lead_sponsor_agency_ind] # 43

        out_publisher = '0'                   # 44
        out_pmid = '0'                        # 45
        out_pmc = '0'                         # 46
        out_pii = '0'                         # 47
        out_publisher_id = '0'                # 48
        out_doi = '0'                         # 49

        # DEAL WITH PUB_DATE                  # 50
        out_pub_date = '0'
        if ',' in row[src_study_first_posted_ind] and len(row[src_study_first_posted_ind].split()) == 3:
            out_pub_date = dp.parse(row[src_study_first_posted_ind], default = dt.datetime(dt.MINYEAR, 1, 1).date(), dayfirst = True).strftime('%Y%m%d')
            out_pub_date = out_pub_date.strip()

        if out_pub_date == '0' or len(out_pub_date) != 8:
            dates_wrong += 1
        # DEAL WITH PUB_DATE                  # 50

        # DEAL WITH TRIAL TITLE               # 51
        if row[src_brief_title_ind] != '0' and row[src_brief_title_ind] != '' and row[src_brief_title_ind] != None:
            out_article_title = row[src_brief_title_ind]
        elif row[src_official_title_ind] != '0' and row[src_official_title_ind] != '' and row[src_official_title_ind] != None:
            out_article_title = row[src_official_title_ind]
        else:
            print 'No Title Found: ', row[src_nct_id_ind]
            continue
        # DEAL WITH TRIAL TITLE               # 51

        countries_iterim = row[src_location_countries_ind].split('|')
        out_article_authors = ', '.join(countries_iterim)        # 52
        if out_article_authors == '' or out_article_authors == ' ' or out_article_authors == None:
            out_article_authors = '0'

        out_article_keywords = '0'             # 53
        out_old_article_type = '0'             # 54
        out_article_citation_number = '0'      # 55
        out_article_category = '0'             # 56
        out_article_access = '0'               # 57
        out_text_type = '0'                    # 58

        out_article_section_compartment = 'STUDY PARAMETERS'    # 59
        out_article_section_original = 'STUDY PARAMETERS'       # 60
        out_article_section_bucket = 'STUDY PARAMETERS'         # 61

        out_article_heading_cat = '0'           # 62
        out_article_type_tag = 'Clinical Study' # 63

        out_total_score_conf = '1'              # 64
        out_total_score_strength_norm = '1'     # 65
        out_relevance = '1'                     # 66
        out_hypothetical_flag = '1'             # 67

        # DEAL WITH PUB YEAR                    # 68
        out_pub_date_year = '0'
        out_pub_date_year = out_pub_date[:4]
        # DEAL WITH PUB YEAR                    # 68

        out_journal_sjr = '0'                   # 69
        out_journal_sjr_quartile = '0'          # 70
        out_journal_hindex = '0'                # 71
        out_journal_categories = '0'            # 72

        # DEAL WITH article_title_reduced, hashcode       # 73, 74
        ct_title = out_article_title.lower()
        out_article_title_reduced = re.sub('[^a-z]+', '', ct_title)
        out_article_hashcode = hashlib.sha256(out_article_title_reduced).hexdigest()
        # DEAL WITH article_title_reduced, hashcode       # 73, 74

        # DEAL WITH source_hashcode             # 75
        source_hash_temp = out_article_hashcode + row[src_nct_id_ind] + row[src_intervention_cui_ind] + row[src_condition_cui_ind] + row[src_intervention_name_ind] + row[src_condition_ind]
        source_hash_temp = source_hash_temp.lower()
        source_hash_temp = source_hash_temp.replace(' ', '')
        out_source_hashcode = hashlib.sha256(source_hash_temp).hexdigest()
        if out_source_hashcode not in seen_source_hashes:
            seen_source_hashes[out_source_hashcode] = 1
        else:
            print 'Duplicate dropped on source hash..', row
            continue
        # DEAL WITH source_hashcode             # 75

        out_cause_category = row[src_intervention_categories_ind]   # 76
        out_cause_concept_cui = row[src_intervention_cui_ind]       # 77

        out_cause_concept_matched = '0'         # 78

        out_effect_category = row[src_condition_categories_ind]     # 79
        out_effect_concept_cui = row[src_condition_cui_ind]         # 80

        out_effect_concept_matched = '0'            # 81
        out_cause_concept_option = '0'              # 82
        out_cause_category_option = '0'             # 83
        out_cause_concept_option_score = '0'        # 84
        out_cause_concept_option_cui = '0'          # 85
        out_cause_event_concept_option = '0'        # 86
        out_cause_category_event_option = '0'       # 87
        out_cause_event_concept_option_score = '0'  # 88
        out_cause_event_concept_option_cui = '0'    # 89
        out_effect_concept_option = '0'             # 90
        out_effect_category_option = '0'            # 91
        out_effect_concept_option_score = '0'       # 92
        out_effect_concept_option_cui = '0'         # 93
        out_effect_event_concept_option = '0'       # 94
        out_effect_category_event_option = '0'      # 95
        out_effect_event_concept_option_score = '0' # 96
        out_effect_event_concept_option_cui = '0'   # 97
        out_cause_concept_secondary = '0'           # 98
        out_cause_concept_secondary_conf = '0'      # 99
        out_cause_category_secondary = '0'          # 100
        out_cause_concept_secondary_cui = '0'       # 101
        out_effect_concept_secondary = '0'          # 102
        out_effect_concept_secondary_conf = '0'     # 103
        out_effect_category_secondary = '0'         # 104
        out_effect_concept_secondary_cui = '0'      # 105
        out_last_update_op = '0'                    # 106

        out_article_pt = 'Clinical Study'           # 107
        out_article_mesh_terms = '0'                # 108
        out_article_mesh_qualifiers = '0'           # 109
        out_mesh_source = '0'                       # 110

        # todo: DEAL WITH out_article_uuid                # 111
        out_article_uuid = row[src_nct_id_ind] + '_'+str(sys.argv[3])+'_'+str(sys.argv[4])
        # DEAL WITH out_article_uuid                # 111

        out_primary_id = row[src_nct_id_ind]        # 112
        out_secondary_id = row[src_secondary_id_ind]    # 113

        out_tertiary_id = '0'                       # 114
        out_data_source = '8'                       # 115
        out_article_type = '3'                      # 116

        out_batch_generation = str(sys.argv[3])           # 117
        out_parse_version = str(sys.argv[4])                    # 118

        out_sem_type = 'UNIDIRECTIONAL'             # 119
        out_type_changes = '0'                      # 120
        out_assoc_switch = '0'                      # 121

        row = [out_filename, sentence_n, sentence_f, out_content_raw, out_is_causal, out_topic, out_connective, out_connective_case, out_connective_type, out_connective_negation, out_connective_aux, out_connective_tempus, out_clause, out_clause_neg, out_clause_aux, out_db_remark, out_cause_phrase,
               out_cause_keyword, out_cause_keyword_display, out_cause_event, out_cause_keyword_NMOD, out_cause_switch, out_cause_concept, out_cause_concept_conf, out_effect_phrase, out_effect_keyword, out_effect_keyword_display, out_effect_event, out_effect_keyword_NMOD, out_effect_switch,
               out_effect_concept, out_effect_concept_conf, out_chaining, out_duplicate, out_cause_clause_type, out_effect_advcl, out_extract_cause_tag, out_RES_ROOT_NMOD_BY, out_ACL_SUCH_AS, out_tuple_order, out_indirect_causality, out_issn, out_journal_title, out_publisher, out_pmid, out_pmc,
               out_pii, out_publisher_id, out_doi, out_pub_date, out_article_title, out_article_authors, out_article_keywords, out_old_article_type, out_article_citation_number, out_article_category, out_article_access, out_text_type, out_article_section_compartment, out_article_section_original,
               out_article_section_bucket, out_article_heading_cat, out_article_type_tag, out_total_score_conf, out_total_score_strength_norm, out_relevance, out_hypothetical_flag, out_pub_date_year, out_journal_sjr, out_journal_sjr_quartile, out_journal_hindex, out_journal_categories,
               out_article_title_reduced, out_article_hashcode, out_source_hashcode, out_cause_category, out_cause_concept_cui, out_cause_concept_matched, out_effect_category, out_effect_concept_cui, out_effect_concept_matched, out_cause_concept_option, out_cause_category_option,
               out_cause_concept_option_score, out_cause_concept_option_cui, out_cause_event_concept_option, out_cause_category_event_option, out_cause_event_concept_option_score, out_cause_event_concept_option_cui, out_effect_concept_option, out_effect_category_option,
               out_effect_concept_option_score, out_effect_concept_option_cui, out_effect_event_concept_option, out_effect_category_event_option, out_effect_event_concept_option_score, out_effect_event_concept_option_cui, out_cause_concept_secondary, out_cause_concept_secondary_conf,
               out_cause_category_secondary, out_cause_concept_secondary_cui, out_effect_concept_secondary, out_effect_concept_secondary_conf, out_effect_category_secondary, out_effect_concept_secondary_cui, out_last_update_op, out_article_pt, out_article_mesh_terms, out_article_mesh_qualifiers,
               out_mesh_source, out_article_uuid, out_primary_id, out_secondary_id, out_tertiary_id, out_data_source, out_article_type, out_batch_generation, out_parse_version, out_sem_type, out_type_changes, out_assoc_switch]

        for ind, item in enumerate(row):
            row[ind] = row[ind].replace('\t', ' ').replace('\n', ' ').strip()
            if row[ind] == ' ' or row[ind] == None or row[ind] == '':
                print row
                print row[ind]
                print ind
                raw_input('wait')

        counter += 1
        writer.writerow(row)

        # if not counter % 5:
        #     writer_test.writerow(row)

print 'DATES WRONG: ', dates_wrong
