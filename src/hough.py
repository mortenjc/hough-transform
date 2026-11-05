import argparse
from collections import defaultdict
from functools import cache
import math
import matplotlib.pyplot as plt
import numpy as np
import scipy
import sys


def readfile(filename: str, n: int):
    D = defaultdict(list)
    with open(filename,"r") as f:
        for i, line in enumerate(f.readlines()):
            if i == 0: # skip legend
                continue
            if i % n == 0:
                p, q, r, f, t = line.strip().split()
                key = f'{int(r):02x}{int(f):02x}{int(t):02x}'
                D[key].append((float(q),float(p)))
    return D


def getxy(D, key):
    return [P for P in D[key]]


def hough_lines_from_points(points, theta_res=1, rho_res=1):
    """
    Detects lines from a list of (x, y) coordinates using Hough Transform.
    
    :param points: List or array of tuples [(x1, y1), (x2, y2), ...]
    :param theta_res: Angle resolution in degrees.
    :param rho_res: Distance resolution in coordinate units.
    """
    if len(points) == 0:
        return [], [], []

    points = np.array(points)
    # x_coords = points[:, 0]
    # y_coords = points[:, 1]

    thetas = np.deg2rad(np.arange(50.0, 140.0, theta_res))
    cos_t = np.cos(thetas)
    sin_t = np.sin(thetas)
    
    #max_dist = int(np.ceil(np.sqrt(np.max(x_coords)**2 + np.max(y_coords)**2)))
    max_dist = 2
    rhos = np.arange(-max_dist, max_dist, rho_res)
    accumulator = np.zeros((len(rhos), len(thetas)), dtype=int)

    for x, y in points:
        current_rhos = x * cos_t + y * sin_t
        
        rho_idxs = np.round((current_rhos + max_dist) / rho_res).astype(int)
        
        for theta_idx, rho_idx in enumerate(rho_idxs):
            if 0 <= rho_idx < len(rhos):
                accumulator[rho_idx, theta_idx] += 1
    return accumulator, thetas, rhos


def find_peaks(arr, N=7):
    local_max = (scipy.ndimage.maximum_filter(arr, size=3) == arr)
    #print('local max', local_max)
    max_indices = np.argwhere(local_max)
    #print('max_indices', max_indices)
    
    max_values = arr[local_max]

    top_n_indices = np.argsort(max_values)[-N:][::-1]
    peak_coords = max_indices[top_n_indices]  # Array of (row, col)
    #peak_vals = max_values[top_n_indices]
    return [(float(x[0]), float(x[1])) for x in peak_coords]


def check_all(D, args):
    bad = 0
    toplot = 0
    keys = list(D.keys())
    print(f'keys in total {len(keys)}')
    res = {}
    for key in keys:
        if toplot != 0 and toplot % 16 == 0:
            plot(res)
            res.clear()
            toplot = 0

        points = getxy(D, key)
        pps = len(points)//7

        acc, thetas, rhos = hough_lines_from_points(points, theta_res=1, rho_res=0.01)
        peaks = find_peaks(acc)

        ths = [x[1] for x in peaks]
        th2 = [float(thetas[int(x)]) for x in ths]
        th3 = [abs(x - 1.570796) for x in th2]
        th4 = [1 if x < 0.07 else 0 for x in th3]
        isbad = sum(th4) != 7
        if  isbad or args.g:
            if isbad:
                print(f'Bad  {bad:3} {key} (pps {pps}): {peaks}')
            else:
                print(f'Good {bad:3} {key} (pps {pps}): {peaks}')
            bad += 1
            toplot += 1
            res[key] =[points, acc, rhos, thetas, peaks]

    return res
 

def plot(results):
    fig, ax = plt.subplots(4, 4, figsize=(20, 15), sharey=False)
    for i, d in enumerate(results):
        points, acc, rhos, thetas, peaks = results[d]
        xi = i // 4
        yi = i % 4

        fig.suptitle(f'Detection of skewed straws', fontsize=16)
        ax[xi, yi].title.set_text(f'Key {d}')
        ax[xi, yi].title.set_fontsize(10)
        ax[xi, yi].scatter([p[1]for p in points], [p[0] for p in points], s=0.5)
        for ri, thi in peaks:
            r2 = rhos[int(ri)]
            th2 = thetas[int(thi)]
            point = (r2 * math.sin(th2), r2 * math.cos(th2))
            slope = math.tan(th2)
            ax[xi, yi].axline(xy1=point, slope=-slope, color='red', linestyle='--', label='Slope=1.5 through (2,3)')
    plt.draw()



def find_nearest_line(point, lines):
    #print(point, lines)
    x, y = point
    best = (-1, -1, -1, -1)
    mindist = 100
    for i, l in enumerate(lines):
        r, a = l
        x0 = r * math.cos(a)
        y0 = r * math.sin(a)
        #print(x0, y0)
        d = math.dist(point, (x0, y0))
        if d < mindist:
            best = (x0, y0, a, i)
            mindist = d
    #print(f'nearest line for point {point} is {best}')

    x0, y0, a, i = best
    x = (x-x0)*math.cos(a) + (y-y0)*math.sin(a) + x0
    y = -(x-x0)*math.sin(a) + (y-y0)*math.cos(a) + y0
    return (x, y, i)




# ------------------------------------------------------------------- demo
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", help = "file to read", type = str, default = "", required=True)
    parser.add_argument("-n", help = "sample every n point", type = int, default = 1)
    parser.add_argument("-r", help = "Ring", type = int, default = 0)
    parser.add_argument("-e", help = "FEN", type = int, default = 0)
    parser.add_argument("-t", help = "Tube", type = int, default = 0)
    parser.add_argument("-i", help = "straw", type = int, default = 0)
    parser.add_argument("-p", help = "plot data", action='store_true')
    parser.add_argument("-a", help = "find all bad lines", action='store_true')
    parser.add_argument("-g", help = "also show good tubes", action='store_true')
    parser.add_argument("-v", help = "verbose", action='store_true')

    args = parser.parse_args()
    if not (args.a or args.p):
        print('Nothing to do ...')
        sys.exit()

    D = readfile(args.f, args.n)
    if args.a:
        print('Finding all bad straws')
        res = check_all(D, args)
        plot(res)
        sys.exit()

    if args.p:
        print('Checking RING {args.r}, FEN {args.e}, Tube {args.t}')
        key = f'{args.r:02x}{args.e:02x}{args.t:02x}'
        points = getxy(D, key)
        if not len(points):
            print('No points to plot for key', key)
            sys.exit()
    
        print(f'points to fit {len(points)}, per straw {len(points)//7}')
        acc, thetas, rhos = hough_lines_from_points(points, theta_res=1, rho_res=0.01)
        peaks = find_peaks(acc)

        lines = []
        fig, ax = plt.subplots(1, 2, figsize=(10, 5), sharey=False)
        fig.suptitle(f'Ring {args.r}, FEN {args.e}, Tube {args.t}', fontsize=16)
        plt.imshow(acc, interpolation='none')

        ax[1].set_xlabel(r'$\theta$ index')
        ax[1].set_ylabel(r'$r$ index')
        #ax[1].set_ylim([150, 350])
        #ax[1].set_xlim([60, 120])
        ax[0].scatter([p[1]for p in points], [p[0] for p in points], s=0.5)
        for ri, thi in peaks:
            r2 = rhos[int(ri)]
            th2 = thetas[int(thi)]
            point = (r2 * math.sin(th2), r2 * math.cos(th2))
            lines.append((round(float(r2),2), round(float(th2),2)))
            
            m = math.tan(th2)
            ax[0].axline(xy1=point, slope=-m, color='red', linestyle='--', label='Slope=1.5 through (2,3)')
            ax[0].scatter(point[0], point[1], c='k')
        print('lines', lines)
        

        corrpts = []
        for p in points:
            cp = find_nearest_line(p, lines)
            if cp[2] == args.i:
                corrpts.append(p)
        #fig, ax = plt.subplots(1, 2, figsize=(10, 5), sharey=False)
        ax[0].scatter([p[1]for p in corrpts], [p[0] for p in corrpts], s=0.5, c='red')
        plt.show()
        sys.exit()


        




