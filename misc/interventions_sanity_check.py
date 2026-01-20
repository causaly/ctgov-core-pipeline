import csv
import sys

csv.field_size_limit(58000000)

file_no_cache = sys.argv[1]

no_cache_mappings = {}
print("Read no cached mm file ...")
output_rows = []
cuis = set()
with open(file_no_cache, 'r') as my_file:
    reader = csv.reader(my_file, delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='', escapechar='\\')

    for idx, row in enumerate(reader):

        if idx == 0:
            # Map column name to their indices
            output_rows.append(row)
            field_index = {}
            for pair in list(enumerate(row)):
                field_index[pair[1]] = pair[0]

        else:
            if not idx % 100000:
                print(idx)
            request = row[field_index["intervention_mm_request"]]
            concept = row[field_index["intervention_concept"]]
            cui = row[field_index["intervention_cui"]]
            cuis.add(cui)
            all_mm = row[field_index["intervention_all_mm"]]
            if request not in no_cache_mappings:
                no_cache_mappings[request] = [concept, cui, request, all_mm]
            else:
                if cui != no_cache_mappings[request][1]:
                    print(request)
                    print(no_cache_mappings[request])
                    print(concept,cui,request, all_mm)


print(len(no_cache_mappings), len(cuis))
