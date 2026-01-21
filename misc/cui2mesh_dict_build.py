import pickle
import sys

mrconso_file = sys.argv[1]
cui2mesh_out_file = sys.argv[2]
prev_cui2mesh_file = sys.argv[3]
cui2mesh_out_file_merged = sys.argv[4]


with open(prev_cui2mesh_file, 'rb') as handle:
    prev_cui2mesh_dict = pickle.load(handle)

mrconso = open(mrconso_file, 'r')
line_counter = 0

cui2mesh_dict = {}

while True:
    line_counter += 1
    if not line_counter % 100000:
        print(line_counter, len(cui2mesh_dict))

    # Get next line from file
    line = mrconso.readline()
    if not line:
        break
    line_vals = line.split("|")
    language = line_vals[1].strip().lower()
    source = line_vals[11].strip()
    ts = line_vals[2].strip()
    ts2 = line_vals[4].strip()
    if language == "eng" and source == "MSH" and ts == "P" and ts2 == "PF":
        cui = line_vals[0]
        d_code = line_vals[13]
        str_atom = line_vals[14]
        if cui not in cui2mesh_dict:
            cui2mesh_dict[cui] = "#####".join([d_code, str_atom])
        else:
            if "#####".join([d_code, str_atom]) != cui2mesh_dict[cui]:
                print("Duplicate ERROR!!")
                print(cui)

print("Lines read: {}".format(line_counter))
mrconso.close()
print("cui2mesh dict size: {}".format(len(cui2mesh_dict)))


with open(cui2mesh_out_file, "wb") as fh:
    pickle.dump(cui2mesh_dict, fh)


# Merge prev_cui2mesh_dict with cui2mesh_dict
counter = 0
for cui in prev_cui2mesh_dict:
    if cui not in cui2mesh_dict:
        cui2mesh_dict[cui] = prev_cui2mesh_dict[cui]
        counter += 1

print("Missing CUI-MESH pairs that were in the previous dictionary and are now added: {}".format(counter))
print("New cui2mesh merged dict size: {}".format(len(cui2mesh_dict)))

with open(cui2mesh_out_file_merged, "wb") as fh:
    pickle.dump(cui2mesh_dict, fh)
