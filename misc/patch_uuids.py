import sys
import csv

in_file = sys.argv[1]
out_file = sys.argv[2]

writer = csv.writer(open(out_file, "w"), delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='')
with open(in_file, 'r', encoding='ISO-8859-1') as my_file:
    reader = csv.reader(my_file, delimiter='\t')

    for idx, row in enumerate(reader):

        if idx == 0:
            fieldIndex = dict()
            for pair in list(enumerate(row)):
                fieldIndex[pair[1]] = pair[0]
            writer.writerow(row)
        else:
            new_row = row[:]
            new_batch_gen = "20231027"
            new_row[fieldIndex["batch_generation"]] = new_batch_gen
            new_row[fieldIndex["article_uuid"]] = "_".join([row[fieldIndex["article_uuid"]].split("_")[0], new_batch_gen, row[fieldIndex["article_uuid"]].split("_")[2]]) 
            writer.writerow(new_row)
