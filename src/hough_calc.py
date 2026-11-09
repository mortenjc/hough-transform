import argparse
import numpy as np
import scipy
import time
import fileops
import plots
import rectify

def hough_lines_from_points_opt(points, theta_res=1, rho_res=1):
    assert len(points)

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



def find_peaks(arr, rhos, thetas, N=7):
    local_max = (scipy.ndimage.maximum_filter(arr, size=3) == arr)
    max_indices = np.argwhere(local_max)
    max_values = arr[local_max]

    top_n_indices = np.argsort(max_values)[-N:][::-1]
    peak_coords = max_indices[top_n_indices]
    #peak_vals = max_values[top_n_indices]
    return [(round(float(rhos[int(x[0])]),3),
             round(float(thetas[int(x[1])]),3)) for x in peak_coords]
     

def get_bad_tubes(D):
    badtubes = {}

    for key in D.keys():
        #print(f'key {key}')
        points = D[key]
        pts_per_straw = len(points)//7  # average

        acc, thetas, rhos = hough_lines_from_points_opt(points, theta_res=1, rho_res=0.01)
        peaks = find_peaks(acc, rhos, thetas)
        #print(peaks)

        ths = [x[1] for x in peaks]
        th3 = [abs(x - 1.570796) for x in ths]
        th4 = [1 if x < 0.07 else 0 for x in th3]
        isbad = sum(th4) != 7
        if  isbad or args.g:
            if isbad:
                print(f'Bad  {len(badtubes):3} {key} (pps {pts_per_straw}): {peaks}')
            else:
                print(f'Good {len(badtubes):3} {key} (pps {pts_per_straw}): {peaks}')
            badtubes[key] = peaks

    return badtubes
 


def main(args):
    t0 = time.time()
    D, n = fileops.readpoints(args.f, args.n)
    t1 = time.time()
    print(f'points: {n}, load time {t1-t0:.1f}')

    tubes = get_bad_tubes(D)
    plots.plot_lines(D, tubes, title="Raw data and derived lines")

    if args.s:
        print('saving straw lines')
        fileops.datasave(tubes, args.s)

def test_calc():
    D = {}
    lines = [(0.1 + n/10, 0.0, np.pi/2 - 0.1) for n in range(7)]
    points = rectify.makepoints(lines, scale=0.0, pts_per_straw=70)
    print(points)
    plots.plot_points(points)
    D['000000'] = points
    tubes = get_bad_tubes(D)
    print(tubes)
    plots.plot_lines(D, tubes)
  
    assert False



# ------------------------------------------------------------------- demo
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", help = "file to read", type = str, default = "", required=True)
    parser.add_argument("-n", help = "sample every n point", type = int, default = 1)
    parser.add_argument("-g", help = "also show good tubes", action='store_true')
    parser.add_argument("-p", help = "plot lines and data", action='store_true')
    parser.add_argument("-s", help = "json file", type = str, default = "")
    args = parser.parse_args()

    assert test_calc()

    main(args)

        




