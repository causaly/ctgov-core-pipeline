import pickle
import sys

mrconso_file = sys.argv[1]
atoms_out_pickle_name = sys.argv[2]

mrconso = open(mrconso_file, 'r')
line_counter = 0

atoms = {}

while True:
    line_counter += 1
    if not line_counter % 100000:
        print(line_counter, len(atoms))

    # Get next line from file
    line = mrconso.readline()
    if not line:
        break
    line_vals = line.split("|")
    language = line_vals[1].strip().lower()
    if language == "eng":
        cui = line_vals[0]
        atom = line_vals[14]
        if cui not in atoms:
            atoms[cui] = [atom]
        else:
            if atom not in atoms[cui]:
                atoms[cui].append(atom)

print("Lines read: {}".format(line_counter))
mrconso.close()
print("atoms dict size: {}".format(len(atoms)))


with open(atoms_out_pickle_name, "wb") as fh:
    pickle.dump(atoms, fh)

atoms_out_pickle_name_python2 = atoms_out_pickle_name.split(".")[0] + ".pkl2"

with open(atoms_out_pickle_name_python2, "wb") as fh:
    pickle.dump(atoms, fh, protocol=2)
