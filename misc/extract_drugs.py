#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import csv
import sys
from lxml import etree

# TODO need to find a better way to deal with default encoding -- still does not run without excerpt below

#writer = csv.writer(open('/Users/asaudabayev/corpus/05_ctgov/20200810/20200810_01_clinicaltrialsgov_xmlstage.csv', "w"), delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='')

writer = csv.writer(open(sys.argv[2], "w"), delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='')

header_row = ['nct_id', 'intervention_type', 'arm_group', 'intervention_name', 'other_name']
writer.writerow(header_row)


data_path = sys.argv[1]

subdirs = [x[0] for x in os.walk(data_path) if x[0] != data_path]

counter = 1
total_counter = 0
no_condition_and_no_intervention_counter = 0
unique_nct_ids = {}

print('nct_id\tunique_arms\tunique_drugs\tunique_pairs\tofficial_title')
# GO ON A SUBDIRECTORY-BY-SUBDIRECTORY BASIS
for subdir in subdirs:
    for file in os.listdir(subdir):

        total_counter += 1

        filename = subdir + '/' + file
        #print 'FILENAME: ', filename

        # THE XML FILES ARE READ IN USING etree.fromstring reader
        infile = open(filename, encoding='utf-8').read()
        art_tag = etree.fromstring(infile)

        #############################################################
        # INITIALIZE ALL FIELDS TO BE EXTRACTED


        all_drugs = []
        all_arms = []
        all_others = []
        official_title = '0'
        # END VARIABLE INITIALIZING
        #############################################################

        for main_tag in art_tag.getchildren():
            if main_tag.tag == 'id_info':
                for study_ids in main_tag.getchildren():
                    if study_ids.tag == 'org_study_id':
                        org_study_id = study_ids.text
                    if study_ids.tag == 'secondary_id':
                        secondary_id = study_ids.text
                    if study_ids.tag == 'nct_id':
                        nct_id = study_ids.text

            if main_tag.tag == 'official_title' and main_tag.text != None:
                official_title = main_tag.text

            if main_tag.tag == 'intervention':
                intervention_types = []
                intervention_names = []
                other_names = ['0']
                arm_groups = ['0']
                for intervention in main_tag.getchildren():
                    if intervention.tag == 'intervention_type' and intervention.text != None:
                        intervention_types.append(intervention.text)
                    if intervention.tag == 'intervention_name' and intervention.text != None:
                        intervention_names.append(intervention.text)
                    if intervention.tag == 'other_name' and intervention.text != None:
                        other_names.append(intervention.text)
                    if intervention.tag == 'arm_group_label' and intervention.text != None:
                        arm_groups.append(intervention.text)

                if len(other_names) > 1:
                    other_names = other_names[1:]
                if len(arm_groups) > 1:
                    arm_groups = arm_groups[1:]
                for arm_group in arm_groups:
                    for intervention_name, intervention_type in zip(intervention_names, intervention_types):
                        for other_name in other_names:
                            intervention_name = intervention_name.encode('ASCII', 'ignore').decode()
                            row = [nct_id, intervention_type, arm_group, intervention_name, other_name]
                            if intervention_type in ['Drug', 'Biological']:
                                all_arms.append(arm_group)
                                all_drugs.append(intervention)
                                if other_name != '0':
                                    all_others.append(f'{intervention}|{other_name}')
                            # all_others.append(other_name)
                            writer.writerow(row)

        print(f'{nct_id}\t{len(set(all_arms))}\t{len(set(all_drugs))}\t{len(set(all_others))}\t{official_title}')
