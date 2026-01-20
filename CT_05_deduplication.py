#!/usr/bin/python
# -*- coding: utf-8 -*-

# THIS IS A POSTMETAMAP DEDUPLICATION SCRIPT FOR CLINICAL TRIALS .GOV

import csv
import sys
csv.field_size_limit(58000000)

# TODO need to find a better way to deal with default encoding -- still does not run without excerpt below
reload(sys)
sys.setdefaultencoding('utf-8')


filename = sys.argv[1] #'/Users/asaudabayev/corpus/05_ctgov/20200810/covid_replaced_20200810_01_clinicaltrialsgov_xmlstage_condition+intervention.csv'

#writer_ok = csv.writer(open('/Users/asaudabayev/corpus/05_ctgov/20200810/deduped_covid_replaced_20200810_01_clinicaltrialsgov_xmlstage_condition+intervention.csv', "w"), delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='')
writer_ok = csv.writer(open(sys.argv[2], "w"), delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='')

seen_combinations = {}
count = 0
total_counter = 0

# NCTid is a unique id assigned for a Clinical Trial
# For each NCTid it only makes sense to have unique DISEASE-INTERVENTION pair
unique_ncts = {}    # This dict holds the unique pairs

# ToDO: create variables with row indices pre-assigned, i.e. nctid_ind = 27 to then access data as row[nctid_ind]
with open(filename, 'r') as my_file:
    reader = csv.reader(my_file, delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='')

    for idx, row in enumerate(reader):

        if idx == 0:
            print row[6], row[13], row[27]
            writer_ok.writerow(row)
            continue

        total_counter += 1

        nct_id = row[27].strip().lower()
        interv_cui = row[13].strip().lower()
        condition_cui = row[6].strip().lower()
        condition = row[4].strip().lower()
        interv = row[11].strip().lower()

        if nct_id not in unique_ncts:
            unique_ncts[nct_id] = 1

        if interv_cui == '0' and condition_cui == '0':
            combination = condition + interv + nct_id
        elif condition_cui == '0':
            combination = condition + interv_cui + nct_id
        elif interv_cui == '0':
            combination = condition_cui + interv + nct_id
        else:
            combination = condition_cui + interv_cui + nct_id

        if combination not in seen_combinations:
            seen_combinations[combination] = 1
            writer_ok.writerow(row)
        else:
            count += 1

print total_counter
print count
print len(unique_ncts)
