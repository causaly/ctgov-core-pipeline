import sys
import csv

in_file = sys.argv[1]

nct_ids = {}
row_cunter = 0
inter_and_cond = 0
no_entities = 0
inter_only = 0
cond_only = 0
unique_conditions = {}
unique_interventions = {}

print()
print("#"*30)
print()

with open(in_file, 'r', encoding='ISO-8859-1') as my_file:
    reader = csv.reader(my_file, delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='',escapechar = '\\')

    for idx, row in enumerate(reader):
        if idx == 0:
            # Map column name to their indices
            fieldIndex = dict()
            for pair in list(enumerate(row)):
                fieldIndex[pair[1]] = pair[0]

        else:

            row_cunter += 1
            #if not idx %100000:
                #print(idx)

            article_uuid = row[fieldIndex["article_uuid"]]
            nct_ids[article_uuid] = [1]
            condition_cui = row[fieldIndex["effect_concept_cui"]]
            intervention_cui = row[fieldIndex["cause_concept_cui"]]

            # Both condition and intervention
            if condition_cui != 0 and condition_cui != "0" and intervention_cui != 0 and intervention_cui != "0":
                inter_and_cond += 1
            # Neither condition nor intervention
            elif ((condition_cui == 0 or condition_cui == "0") and (intervention_cui == 0 or intervention_cui == "0")):
                no_entities += 1
            # Only condition
            elif ((condition_cui != 0 and condition_cui != "0") and (intervention_cui == 0 or intervention_cui == "0")):
                cond_only += 1
            # Only Intervention
            elif ((condition_cui == 0 or condition_cui == "0") and (intervention_cui != 0 and intervention_cui != "0")):
                inter_only += 1

            if condition_cui != 0 and condition_cui != "0":
                unique_conditions[condition_cui] = 1

            if intervention_cui != 0 and intervention_cui != "0":
                unique_interventions[intervention_cui] = 1


print("Number of uploaded documents: {}".format(len(nct_ids)))
print("Total number of rows: {}".format(row_cunter))
print("Number of extracted relationships (i.e., with both interventions and indications): {}".format(inter_and_cond))
print("Number relationships with non recognized entities: {}".format(no_entities))
print("Number relationships with recognized Intervention only: {}".format(inter_only))
print("Number relationships with recognized Indication only: {}".format(cond_only))
print("Number of unique recognized entities (Interventions): {}".format(len(unique_interventions)))
print("Number of unique recognized entities (Indications): {}".format(len(unique_conditions)))
