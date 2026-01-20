import sys
import pickle5 as pickle
import csv

csv.field_size_limit(58000000)

cui_to_mesh_filename = sys.argv[3]

with open(cui_to_mesh_filename, 'rb') as handle:
    cui_to_mesh = pickle.load(handle)

print(cui_to_mesh['C0018801'])

filename = sys.argv[1]

uuid_mesh_dict = {}

with open(filename, 'r',  encoding='ISO-8859-1') as my_file:
    reader = csv.reader(my_file, delimiter='\t')

    for idx, row in enumerate(reader):

        if idx == 0:
            cause_concept_cui_ind = row.index('cause_concept_cui')
            effect_concept_cui_ind = row.index('effect_concept_cui')
            article_uuid_ind = row.index('article_uuid')

            continue

        if not idx % 100000:
            print(idx)

        article_uuid = row[article_uuid_ind]

        if article_uuid not in uuid_mesh_dict:
            uuid_mesh_dict[article_uuid] = []

        if row[cause_concept_cui_ind] != '0' and row[cause_concept_cui_ind].strip() != '' and row[cause_concept_cui_ind] != None:
            if row[cause_concept_cui_ind] in cui_to_mesh:
                if cui_to_mesh[row[cause_concept_cui_ind]].split('#####')[-1] not in uuid_mesh_dict[article_uuid]:
                    uuid_mesh_dict[article_uuid].append(cui_to_mesh[row[cause_concept_cui_ind]])
                    # uuid_mesh_dict[article_uuid].append(cui_to_mesh[row[cause_concept_cui_ind]].split('#####')[-1])

        if row[effect_concept_cui_ind] != '0' and row[effect_concept_cui_ind].strip() != '' and row[cause_concept_cui_ind] != None:
            if row[effect_concept_cui_ind] in cui_to_mesh:
                if cui_to_mesh[row[effect_concept_cui_ind]].split('#####')[-1] not in uuid_mesh_dict[article_uuid]:
                    uuid_mesh_dict[article_uuid].append(cui_to_mesh[row[effect_concept_cui_ind]])

print('Dict generated')
writer_0 = csv.writer(open(sys.argv[2], 'w'), delimiter='\t', quoting = csv.QUOTE_NONE, quotechar='')

with open(filename, 'r',  encoding='ISO-8859-1') as my_file:
    reader = csv.reader(my_file, delimiter='\t')

    for idx, row in enumerate(reader):

        if idx == 0:
            article_mesh_index = row.index('article_mesh_terms')
            article_uuid_ind = row.index('article_uuid')

            writer_0.writerow(row)
            continue


        article_uuid = row[article_uuid_ind]
        if article_uuid in uuid_mesh_dict and len(uuid_mesh_dict[article_uuid]) > 0:
            article_mesh = uuid_mesh_dict[article_uuid]
            row[article_mesh_index] = '|'.join(article_mesh)
        else:
            row[article_mesh_index] = '0'

        writer_0.writerow(row)
