import argparse
from collections import defaultdict
import math
import matplotlib.pyplot as plt
import numpy as np
import scipy
import sys
import time
import rectify
import plots



# looks like q is y and p is x # TODO
def readfile(filename: str, n: int):
    npts = 0
    D = defaultdict(list)
    with open(filename,"r") as f:
        for i, line in enumerate(f.readlines()):
            if i == 0: # skip legend
                continue
            if i % n == 0:
                npts += 1
                p, q, r, f, t = line.strip().split()
                key = f'{int(r):02x}{int(f):02x}{int(t):02x}'
                D[key].append((float(q),float(p)))
    return D, npts


def getxy(D, key):
    return D[key]


def hough_lines_from_points_opt(points, theta_res=1, rho_res=1):
    if len(points) == 0:
        return [], [], []

    points = np.asarray(points, dtype=float)

    thetas = np.deg2rad(np.arange(50.0, 140.0, theta_res))
    n_theta = len(thetas)

    max_dist = 2
    rhos = np.arange(-max_dist, max_dist, rho_res)
    n_rho = len(rhos)

    # All rho values at once: (N, 2) @ (2, T) -> (N, T)
    trig = np.vstack((np.cos(thetas), np.sin(thetas)))
    current_rhos = points[:, :2] @ trig

    rho_idxs = np.rint((current_rhos + max_dist) / rho_res).astype(np.intp)

    # Keep only in-range votes, then count them all in one bincount call
    theta_idxs = np.broadcast_to(np.arange(n_theta), rho_idxs.shape)
    valid = (rho_idxs >= 0) & (rho_idxs < n_rho)
    flat = rho_idxs[valid] * n_theta + theta_idxs[valid]

    accumulator = np.bincount(flat, minlength=n_rho * n_theta)
    accumulator = accumulator.reshape(n_rho, n_theta).astype(int, copy=False)

    return accumulator, thetas, rhos


# def hough_lines_from_points(points, theta_res=1, rho_res=1):
#     if len(points) == 0:
#         return [], [], []

#     points = np.array(points)

#     thetas = np.deg2rad(np.arange(50.0, 140.0, theta_res))
#     cos_t = np.cos(thetas)
#     sin_t = np.sin(thetas)
    
#     #max_dist = int(np.ceil(np.sqrt(np.max(x_coords)**2 + np.max(y_coords)**2)))
#     max_dist = 2
#     rhos = np.arange(-max_dist, max_dist, rho_res)
#     accumulator = np.zeros((len(rhos), len(thetas)), dtype=int)

#     for x, y in points:
#         current_rhos = x * cos_t + y * sin_t
        
#         rho_idxs = np.round((current_rhos + max_dist) / rho_res).astype(int)
        
#         for theta_idx, rho_idx in enumerate(rho_idxs):
#             if 0 <= rho_idx < len(rhos):
#                 accumulator[rho_idx, theta_idx] += 1
#     return accumulator, thetas, rhos


def find_peaks(arr, rhos, thetas, N=7):
    local_max = (scipy.ndimage.maximum_filter(arr, size=3) == arr)
    max_indices = np.argwhere(local_max)
    max_values = arr[local_max]

    top_n_indices = np.argsort(max_values)[-N:][::-1]
    peak_coords = max_indices[top_n_indices]
    #peak_vals = max_values[top_n_indices]
    return [(round(float(rhos[int(x[0])]),3),
             round(float(thetas[int(x[1])]),3)) for x in peak_coords]
     

def check_all(D, plot_good=False):
    bad = 0
    refval = 1.570796
    keys = list(D.keys())
    print(f'keys in total {len(keys)}')
    res = {}
    for key in keys:
        points = getxy(D, key)
        pps = len(points)//7

        acc, thetas, rhos = hough_lines_from_points_opt(points, theta_res=1, rho_res=0.01)
        peaks = find_peaks(acc, rhos, thetas)

        ths = [x[1] for x in peaks]
        th3 = [abs(x - refval) for x in ths]
        th4 = [1 if x < 0.07 else 0 for x in th3]
        isbad = sum(th4) != 7
        if  isbad or plot_good:
            if isbad:
                bad += 1
                print(f'Bad  {bad:3} {key} (pps {pps}): {peaks}')
            else:
                print(f'Good {bad:3} {key} (pps {pps}): {peaks}')
            res[key] =[points, peaks]
    return res
 

def plot(results):
    for i, d in enumerate(results):
        if i == 0 or i % 16 == 0:
            fig, ax = plt.subplots(4, 4, figsize=(20, 15), sharey=False)
            fig.suptitle(f'Detection of skewed straws #{i//16}', fontsize=16)

        points, peaks = results[d]
        xi = (i%16) // 4
        yi = (i%16) % 4

        ax[xi, yi].title.set_text(f'Key {d}')
        ax[xi, yi].title.set_fontsize(10)
        ax[xi, yi].scatter([p[1]for p in points], [p[0] for p in points], s=0.5)
        for r2, th2 in peaks:
            point = (r2 * math.sin(th2), r2 * math.cos(th2))
            slope = math.tan(th2)
            ax[xi, yi].axline(xy1=point, slope=-slope, color='red',
                              linestyle='--', label='Slope=1.5 through (2,3)')
    plt.show()



def find_nearest_line(point, lines):
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


def test_angles():
    for i in range(10):
        ang = np.pi/2 - 0.05*i
        lines = [(0.1 + n/10, 0.0, ang) for n in range(7)]
        # points are (y, x)
        points = rectify.makepoints(lines, scale=0.005)

        D = {}
        key = '010203'
        D[key] = points
        res = check_all(D, True)
        fitted_lines = res[key][1]
        fitang = fitted_lines[0][1]
        assert abs(ang + fitang - np.pi) < 0.01
        # title = f'line: {ang:.3} ({np.rad2deg(ang):5.3} deg), fitted {fitang:.3} ({np.rad2deg(fitang):5.3} deg)'
        # plots.points_lines(points=points, lines=fitted_lines, title=title)


def test_vertical_lines():
    ang = np.pi/2
    lines = [(0.1 + n/10, 0.0, ang) for n in range(7)]

    # points are (y, x)
    points = rectify.makepoints(lines, scale=0.005)

    D = {}
    key = '010203'
    D[key] = points
    res = check_all(D, True)
    fitted_lines = res[key][1]
    a = sum([x[0] for x in fitted_lines])
    assert 2.799 < a < 2.801
    assert ang - 0.001 < np.pi/2 < ang + 0.001
    #assert all((fitted_lines[0][1] == x[1] for x in fitted_lines))
    # fitang = fitted_lines[0][1]
    # title = f'line: {ang:.3} ({np.rad2deg(ang):5.3} deg), fitted {fitang:.3} ({np.rad2deg(fitang):5.3} deg)'
    # plots.points_lines(points=points, lines=fitted_lines, title=title)



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
    parser.add_argument("--test", help = "run tests", action='store_true')
    parser.add_argument("-v", help = "verbose", action='store_true')
    args = parser.parse_args()

    if args.test:
        test_vertical_lines()
        test_angles()
        sys.exit()

    if not (args.a or args.p):
        print('Nothing to do ...')
        sys.exit()

    t0 = time.time()
    D, n = readfile(args.f, args.n)
    t1 = time.time()
    if args.a:
        print('Finding all bad straws')
        res = check_all(D)
        t2 = time.time()
        print(f'Load time {t2-t1:.1f}, process time {t2-t1:.1f}, pps {n/(t2-t1):.1f}')
        plot(res)
        print('exiting ...')
        sys.exit()

    if args.p:
        print('Checking RING {args.r}, FEN {args.e}, Tube {args.t}')
        key = f'{args.r:02x}{args.e:02x}{args.t:02x}'
        points = getxy(D, key)
        if not len(points):
            print('No points to plot for key', key)
            sys.exit()
    
        print(f'points to fit {len(points)}, per straw {len(points)//7}')
        acc, thetas, rhos = hough_lines_from_points_opt(points, theta_res=1, rho_res=0.01)
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


        




