from collections import defaultdict
import json


def save_lines(filename, dict):
    with open(filename, "w") as f:
        json.dump(dict, f, indent=4)


def load_lines(filename):
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
            key = f'{int(r):02x}{int(f):02x}{int(t):02x}'
            D[key].append((float(x),float(y)))
    return D, npts