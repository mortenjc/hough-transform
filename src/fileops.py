from collections import defaultdict
import json


def save_data(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


def load_data(filename):
    with open(filename, "r") as f:
        data = json.load(f)
    return data


# read (x,y) from ar51 dump format into dictionary
def readfile(filename: str):
    npts = 0
    D = defaultdict(list)
    with open(filename, "r") as f:
        for i, line in enumerate(f.readlines()):
            if i == 0: # skip legend
                continue
            npts += 1
            x, y, r, f, t = line.strip().split()
            key = f'{int(r):02}_{int(f):02}_{int(t):02}'
            D[key].append((float(x),float(y)))
    return D, npts