import pickle
import sys

mrconso_file = sys.argv[1]
cui2mesh_out_file = sys.argv[2]

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

