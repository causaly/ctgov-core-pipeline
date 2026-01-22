import sys
import pickle
import csv

reload(sys)
sys.setdefaultencoding('utf-8')

input_filename = sys.argv[1]


dictionaryDir = '/tools/metathesaurus_files/2025AB_data/'
print("Loading cui_to_cat dictionary...")
with open(dictionaryDir + '2025AB_cui_to_cat.pkl2', 'rb') as handle:
    cui_to_cat = pickle.load(handle)

print("Done loading cui_to_cat dictionary")

print("Reading input file...")

seen_cui = set()
with open(input_filename, 'r') as my_file:
    reader = csv.reader(my_file, delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='')

    for idx, row in enumerate(reader):

        if idx == 0:
            
            cause_concept_cui_ind = row.index('cause_concept_cui')
            effect_concept_cui_ind = row.index('effect_concept_cui')
            
        else:
            cause_concept_cui = row[cause_concept_cui_ind]
            effect_concept_cui = row[effect_concept_cui_ind]
            if cause_concept_cui == '0' or effect_concept_cui == '0':
                continue
            if cause_concept_cui not in cui_to_cat and cause_concept_cui not in seen_cui:
                print(cause_concept_cui)
                seen_cui.add(cause_concept_cui)
            if effect_concept_cui not in cui_to_cat and effect_concept_cui not in seen_cui:
                print(effect_concept_cui)
                seen_cui.add(effect_concept_cui)