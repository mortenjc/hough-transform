import numpy as np
import matplotlib.pyplot as plt
import argparse
from collections import defaultdict
import fileops
import plots
import math


# ideal x coordinates for lines
positions = [1/8 + n/8 for n in range(7)]


def findnearest(x, y, lines):
    r = np.asarray([x[0] for x in lines])
    a = np.asarray([x[1] for x in lines])
    #print(r, a)
    lx = r*np.sin(a)
    ly = -r*np.cos(a)

    angs = np.arctan2(y-ly,x-lx)
    index = np.argmin(np.abs(angs-a))
    return index


def correct(x,y,lines, index):
    assert len(lines) == 7
    ph = np.pi/2
    r, theta = lines[index]

    cx = r
    cy = 0.0
    rota = (ph - theta)

    xp = (x-cx)*np.cos(rota) - (y-cy)*np.sin(rota) + cx
    yp = (x-cx)*np.sin(rota) + (y-cy)*np.cos(rota) + cy
    #print(f'r,theta (rota): {r},{theta}({rota}) - x,y {x},{y}, cx, cy {cx:.4f},{cy:.4f}: final x,y {xp:.4f},{yp:.4f}')
    return (xp, yp)


def main(args, points, lines):
    # data generator
    n = args.p * len(lines)

    # plotting
    ptsz=2000/n
    cols = ['r', 'm', 'y', 'g', 'b', 'c', 'k']

    CP = defaultdict(list)
    CPR = defaultdict(list)
    for x, y in points:
        index = findnearest(x, y, lines)
        xp, yp = correct(x,y, lines, index)
        CP[index].append((x, y))
        CPR[index].append((xp, yp))


    assert len(CP.keys()) == len(CPR.keys())
    for key in CP.keys(): # CPR should have the same keys
        plt.subplot(1,2,1).scatter([x[0] for x in CP[key]], [x[1] for x in CP[key]], marker ='.', s=ptsz, color=cols[key])
        plt.subplot(1,2,2).scatter([x[0] for x in CPR[key]], [x[1] for x in CPR[key]], marker ='.', s=ptsz, color=cols[key])

    xa = [l[0] for l in lines]
    ya = [l[1] for l in lines]
    xb = [l[0] + np.cos(l[2]) for l in lines]
    yb = [l[1] + np.sin(l[2]) for l in lines]

    plt.subplot(1,2,1).scatter(xa,ya, color='k', marker ='+')
    plt.subplot(1,2,1).scatter(xb,yb, color='k', marker ='+')

    for i in range(len(lines)):
        plt.axline((xa[i],ya[i]), (xb[i], yb[i]), color=cols[i], linestyle='-')
    plt.xlim((-0.1, 1.1))
    plt.ylim((-0.1, 1.1))
    plt.show()


def makepoints(lines, scale=0.01, pts_per_straw=1000):
    # stupid and clumpsy random data generator
    pps = pts_per_straw
    pts = []
    for x,y,a in lines:
        r = np.random.uniform(0.05, 0.95, pps)
        dr = np.random.normal(scale=scale, size=pps*2).reshape(-1,2)
        for i in range(pps):
            dx, dy = dr[i]
            xx =  (x + dx + r[i]*np.cos(a)).item()
            yy =  (y + dy + r[i]*np.sin(a)).item()
            pts.append((yy,xx))
    return pts


def makelines():
    la, lb = np.sort(np.random.uniform(0.0, 1.0, 2))
    ha, hb = np.sort(np.random.uniform(0.0, 1.0, 2))

    x1 = np.linspace(la, lb, 7)
    x2 = np.linspace(ha, hb, 7)
    a = np.atan2(1, x2 - x1)
    return [(x1[i], 0.0, a[i]) for i in range(7)]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", help = "data file to read", type = str, default = "", required=True)
    parser.add_argument("-k", help = "check single key", type = str, default = "")
    parser.add_argument("-l", help = "lines", type = str, default = "")
    args = parser.parse_args()

    if args.l:
        L = fileops.load_data(args.l)
    else:
        L = {}

    D, n = fileops.readfile(args.f)



if args.k:
    mjc = {}
    key = args.k
    points = D[key]
    lines = L[key]
    plots.points_lines({key:(points, L[key])}, key)
    
    res = {}
    tmp = []
    for x, y in points:
        i = findnearest(x,y,lines)
        xc, yc = correct(x, y, lines, i)
        tmp.append([xc,yc])
    res[key] = (tmp, lines)
    plots.points_lines(res, key)
    sys.exit()

res = {}
for key in L:
    tmp = []
    points = D[key]
    lines = L[key]
    for x,y in points:
        i = findnearest(x,y,lines)
        xc, yc = correct(x, y, lines, i)
        tmp.append([xc,yc])
    res[key] = (tmp, lines)

plots.tiled_lines(res, plotlines=False)
