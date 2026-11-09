import numpy as np
import matplotlib.pyplot as plt
import argparse
from collections import defaultdict


# ideal x coordinates for lines
positions = [1/8 + n/8 for n in range(7)]


def findnearest(x, y, lines):
    lx = np.asarray([x[0] for x in lines])
    ly = np.asarray([x[1] for x in lines])
    la = np.asarray([x[2] for x in lines])

    angs = np.arctan2(y-ly,x-lx)
    index = np.argmin(np.abs(angs-la))
    return index


def correct(x,y,lines, index):
    x0, y0, a = lines[index]
    cx = x0 + np.cos(a)/2
    cy = y0 + np.sin(a)/2
    ph = np.pi/2
    a2 = (ph - a)
    xp = (x-cx)*np.cos(a2) - (y-cy)*np.sin(a2) + positions[index]
    yp = (x-cx)*np.sin(a2) + (y-cy)*np.cos(a2) + cy
    return (xp, yp)





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
            xx = min(max(xx, 0.05), 0.95)
            yy = min(max(yy, 0.05), 0.95)
            pts.append((xx,yy))
    return pts


# lines are returned as (x, y, angle) NOT (r, theta)
def makelines():
    la, lb = np.sort(np.random.uniform(0.0, 1.0, 2))
    ha, hb = np.sort(np.random.uniform(0.0, 1.0, 2))

    x1 = np.linspace(la, lb, 7)
    x2 = np.linspace(ha, hb, 7)
    a = np.atan2(1, x2 - x1)
    return [(x1[i], 0.0, a[i]) for i in range(7)]


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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", help = "seed", type = int, default = 42)
    parser.add_argument("-p", help = "points per straw", type = int, default = 1000)
    parser.add_argument("-n", help = "number of runs", type = int, default = 1)
    args = parser.parse_args()

    np.random.seed(args.s)

    for cal in range(args.n):
        lines = makelines()
        points = makepoints(lines)
        main(args, points, lines)