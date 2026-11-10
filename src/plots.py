import matplotlib.pyplot as plt
import math


def points_lines(points=[], lines=[], title='', fontsize=8):
    fig, ax = plt.subplots(1, 1, figsize=(5, 4), sharey=False)
    fig.suptitle(title, fontsize=fontsize)
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    if points:
        ax.scatter(y, x, s=0.5)
    if lines:
        for r2, th2, in lines:
            point = (r2 * math.sin(th2), r2 * math.cos(th2))
            slope = math.tan(th2)
            ax.axline(xy1=point, slope=-slope, color='red', linestyle='-')
    ax.set_xlim(0.0, 1.0)
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    plt.show()
