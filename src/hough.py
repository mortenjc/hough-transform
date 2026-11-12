import argparse
import math
import matplotlib.pyplot as plt
import numpy as np
import scipy
import sys
import time
import rectify
import plots
import fileops


def getxy(D, key):
    return D[key]


def hough_lines_from_points_opt(points, theta_res=1, rho_res=1):
    if len(points) == 0:
        return [], [], []

    points = np.asarray(points, dtype=float)

    thetas = np.deg2rad(np.arange(40.0, 140.0, theta_res))
    n_theta = len(thetas)

    max_dist = 2
    rhos = np.arange(-max_dist, max_dist, rho_res)
    n_rho = len(rhos)

    # All rho values at once: (N, 2) @ (2, T) -> (N, T)
    trig = np.vstack((np.sin(thetas), -np.cos(thetas)))
    current_rhos = points[:, :2] @ trig

    rho_idxs = np.rint((current_rhos + max_dist) / rho_res).astype(np.intp)

    # Keep only in-range votes, then count them all in one bincount call
    theta_idxs = np.broadcast_to(np.arange(n_theta), rho_idxs.shape)
    valid = (rho_idxs >= 0) & (rho_idxs < n_rho)
    flat = rho_idxs[valid] * n_theta + theta_idxs[valid]

    accumulator = np.bincount(flat, minlength=n_rho * n_theta)
    accumulator = accumulator.reshape(n_rho, n_theta).astype(int, copy=False)

    return accumulator, thetas, rhos


def hough_lines_from_points(points, theta_res=1, rho_res=1):
    if len(points) == 0:
        return [], [], []

    points = np.array(points)

    thetas = np.deg2rad(np.arange(50.0, 140.0, theta_res))
    cos_t = np.cos(thetas)
    sin_t = np.sin(thetas)
    
    max_dist = 1.5
    rhos = np.arange(-max_dist, max_dist, rho_res)
    accumulator = np.zeros((len(rhos), len(thetas)), dtype=int)

    for x, y in points:
        current_rhos = abs(x * sin_t - y * cos_t)
        
        rho_idxs = np.round((current_rhos + max_dist) / rho_res).astype(int)
        
        for theta_idx, rho_idx in enumerate(rho_idxs):
            if 0 <= rho_idx < len(rhos):
                accumulator[rho_idx, theta_idx] += 1
    return accumulator, thetas, rhos


def check_points(points, N=7):
    acc, thetas, rhos = hough_lines_from_points_opt(points, theta_res=1, rho_res=0.01)

    local_max = (scipy.ndimage.maximum_filter(acc, size=3) == acc)
    max_indices = np.argwhere(local_max)
    max_values = acc[local_max]

    top_n_indices = np.argsort(max_values)[-N:][::-1]
    peak_coords = max_indices[top_n_indices]
    #peak_vals = max_values[top_n_indices]
    return [(round(float(rhos[int(x[0])]),3),
             round(float(thetas[int(x[1])]),3)) for x in peak_coords]


def are_skewed(lines, tolerance=0.07):
    return not all([ abs(l[1]-np.pi/2) < tolerance for l in lines ])


# ------------------------------------------------------------------- demo
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", help = "file to read", type = str, default = "", required=True)
    parser.add_argument("-a", help = "find all bad lines", action='store_true')
    parser.add_argument("-p", help = "plot results", action='store_true')
    #parser.add_argument("-g", help = "also show good tubes", action='store_true')
    parser.add_argument("-s", help = "save lines", type = str, default = "")
    parser.add_argument("-t", help = "line skew tolerance (deg)", type = float, default = 1.0)
    args = parser.parse_args()

    D, n = fileops.readfile(args.f)

    args.t = np.deg2rad(args.t)

    fitted_lines = {}
    res = {}
    for key in D:
        points = D[key]
        lines = check_points(points)

        if are_skewed(lines, tolerance=args.t):
            print(key, lines)
            fitted_lines[key] = lines
            res[key] = (points, lines)
            #plots.points_lines(points, lines, title=f'{key}')

    if args.p:
        plots.tiled(res, title='Bad tubes ')

    if args.s:
        fileops.save_lines(args.s, fitted_lines)
