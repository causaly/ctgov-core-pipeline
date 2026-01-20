import sys
import csv
csv.field_size_limit(58000000)
import os

input_file = sys.argv[1]
output_rows = []
row_index = 0
chunk_index = 0
chunk_size = int(sys.argv[2])


input_filename, file_extension = os.path.splitext(input_file)


counter = 0
with open(input_file, 'r') as my_file:

    reader = csv.reader(my_file, delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='',escapechar = '\\')
    for idx,row in enumerate(reader):


        if idx == 0:
            header = row
            continue
        if len(row) != len(header):
           counter += 1
           continue
        if (idx % chunk_size) != 0:
            output_rows.append(row)
        else:
            output_rows.append(row)
            print(chunk_index)
            #output_rows = [start_row] + output_rows
            w = csv.writer(open(input_filename + '_part' + str(chunk_index)+'.tsv', 'w'), delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='',escapechar = '\\')
            w.writerow(header)
            w.writerows(output_rows)
            output_rows = []
            chunk_index += 1

if len(output_rows) > 0:
    w = csv.writer(open(input_filename + '_part' + str(chunk_index)+'.tsv', 'w'),delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='',escapechar = '\\')
    w.writerow(header)
    w.writerows(output_rows)

print(counter)
