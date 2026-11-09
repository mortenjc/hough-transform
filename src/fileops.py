import json
from collections import defaultdict


def datasave(data, filename):
    with open(filename, 'w') as f:
        f.write(json.dumps(data))


def dataload(filename):
    with open(filename) as f:
        pet = json.loads(f.read())
    return pet


def readpoints(filename: str, n: int):
    npts = 0
    D = defaultdict(list)
    with open(filename,"r") as f:
        for i, line in enumerate(f.readlines()):
            if i == 0: # skip legend
                continue
            if i % n == 0:
                npts += 1
                # q = x, p = y
                p, q, r, f, t = line.strip().split()
                key = f'{int(r):02x}{int(f):02x}{int(t):02x}'
                D[key].append((float(q),float(p)))
    return D, npts


if __name__ == '__main__':

    D = {'080001' : [(1,2), (2,3)]}
    datasave(D, 'deleteme.json')

    B = dataload('deleteme.json')
    assert B['080001'][0][1] == 2


