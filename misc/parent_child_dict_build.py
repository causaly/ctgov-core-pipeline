import pickle
import sys

mrrel_file = sys.argv[1]
parents_out_pickle_name = sys.argv[2]
children_out_pickle_name = sys.argv[3]

mrrel = open(mrrel_file, 'r')
line_counter = 0

children = {}
parents = {}


while True:
    line_counter += 1
    if not line_counter % 100000:
        print(line_counter, len(children), len(parents))

    # Get next line from file
    line = mrrel.readline()
    if not line:
        break
    line_vals = line.split("|")
    rel = line_vals[3].strip().lower()
    if rel in ["par", "chd", "rb", "rn"]:
        cui1 = line_vals[0]
        cui2 = line_vals[4]
        rel_source = line_vals[11]
        cui2_source = "%".join([cui2, rel_source])
        if rel in ["par", "rb"]:
            if cui1 not in parents:
                parents[cui1] = [cui2_source]
            else:
                if cui2_source not in parents[cui1]:
                    parents[cui1].append(cui2_source)
        elif rel in ["chd", "rn"]:
            if cui1 not in children:
                children[cui1] = [cui2_source]
            else:
                if cui2_source not in children[cui1]:
                    children[cui1].append(cui2_source)

print("Lines read: {}".format(line_counter))
mrrel.close()
print("children dict size: {}".format(len(children)))
print("parents dict size: {}".format(len(parents)))

with open(parents_out_pickle_name, "wb") as fh:
    pickle.dump(parents, fh)

parents_out_pickle_name_python2 = parents_out_pickle_name.split(".")[0] + ".pkl2"

with open(parents_out_pickle_name_python2, "wb") as fh:
    pickle.dump(parents, fh, protocol=2)


with open(children_out_pickle_name, "wb") as fh:
    pickle.dump(children, fh)

children_out_pickle_name_python2 = children_out_pickle_name.split(".")[0] + ".pkl2"

with open(children_out_pickle_name_python2, "wb") as fh:
    pickle.dump(children, fh, protocol=2)
