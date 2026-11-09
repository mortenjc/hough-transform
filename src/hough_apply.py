import argparse
import math
import numpy as np
import scipy
import sys
import time
import fileops
import plots


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
     

def get_bad_tubes(args, D):
    badtubes = {}
    keys = list(D.keys())

    for key in keys:
        points = D[key]
        pps = len(points)//7

        acc, thetas, rhos = hough_lines_from_points_opt(points, theta_res=1, rho_res=0.01)
        peaks = find_peaks(acc, rhos, thetas)

        ths = [x[1] for x in peaks]
        th3 = [abs(x - 1.570796) for x in ths]
        th4 = [1 if x < 0.07 else 0 for x in th3]
        isbad = sum(th4) != 7
        if  isbad or args.g:
            if isbad:
                print(f'Bad  {len(badtubes):3} {key} (pps {pps}): {peaks}')
            else:
                print(f'Good {len(badtubes):3} {key} (pps {pps}): {peaks}')
            badtubes[key] = peaks

    return badtubes
 

def correct_point(point, lines):
    x, y = point
    best = (-1, -1, -1, -1)
    mindist = 100
    for i, l in enumerate(lines):
        r, a = l
        x0 = r * math.cos(a)
        y0 = r * math.sin(a)
        d = math.dist(point, (x0, y0))
        if d < mindist:
            best = (x0, y0, a, i)
            mindist = d
    #print(f'nearest line for point {point} is {best}')
    #plots.debug(point, best)

    x0, y0, a, i = best
    x2 =  (x - x0) * math.cos(a) + (y - y0) * math.sin(a) + x0
    y2 = -(x - x0) * math.sin(a) + (y - y0) * math.cos(a) + y0
    #print(f'({x},{y}) -> ({x2},{y2})')
    return (x2, y2, i)


def find_all(args, D, n):
    t1 = time.time()
    tubes = get_bad_tubes(args, D)
    t2 = time.time()
    print(f'process time {t2-t1:.1f}, pps {n/(t2-t1):.1f}')
    return tubes


def correct_all(args, D, tubes):
    corrected = {}
    for key in tubes:
        cpoints = []
        points = D[key]
        #print(f'#1 key {key}, points {len(points)}')
        for x,y in points:
            xc, yc, ic = correct_point((x,y), tubes[key])
            #cpoints.append((xc, yc))
            cpoints.append((x, y))
        corrected[key] = cpoints
    return corrected
       


def main(args):
    t0 = time.time()
    D, n = fileops.readpoints(args.f, args.n)
    t1 = time.time()
    print(f'points: {n}, load time {t1-t0:.1f}')

    if args.a:
        tubes = find_all(args, D, n)
        if args.s:
            fileops.datasave(tubes, args.s)
    elif args.c: # correct
        if not args.s:
            print(f'error: -s option is required')
            sys.exit()
        tubes = fileops.dataload(args.s)
        plots.plot_lines(D, tubes)
        #print(tubes)
        res = correct_all(args, D, tubes)
        plots.plot_lines(res, tubes)
        #print(res)
        #plots.plot_corrected(res, tubes)
    else:
        print(f'use either option -a (analyse all) or -c (correct all)')


# ------------------------------------------------------------------- demo
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", help = "file to read", type = str, default = "", required=True)
    parser.add_argument("-n", help = "sample every n point", type = int, default = 1)
    parser.add_argument("-a", help = "find all bad lines", action='store_true')
    parser.add_argument("-c", help = "correct bad lines", action='store_true')
    parser.add_argument("-g", help = "also show good tubes", action='store_true')
    #parser.add_argument("-v", help = "verbose", action='store_true')
    parser.add_argument("-s", help = "json file", type = str, default = "")

    args = parser.parse_args()

    main(args)

        




