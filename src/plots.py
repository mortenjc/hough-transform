import matplotlib.pyplot as plt
import math
import numpy as np


# def points_lines(points=[], lines=[], title='', fontsize=8):
#     fig, ax = plt.subplots(1, 1, figsize=(5, 4), sharey=False)
#     fig.suptitle(title, fontsize=fontsize)
#     x = [p[0] for p in points]
#     y = [p[1] for p in points]
#     if points:
#         ax.scatter(x, y, s=0.5)
#     if lines:
#         for r2, th2, in lines:
#             point = (r2 * math.sin(th2), -r2 * math.cos(th2))
#             slope = math.tan(th2)
#             ax.axline(xy1=point, slope=slope, color='red', linestyle='-')
#     ax.set_xlim(0.0, 1.0)
#     ax.set_xlim(0.0, 1.0)
#     ax.set_ylim(0.0, 1.0)
#     plt.show()


def tiled_accumulator(results, title='', fontsize=16):
    for i, key in enumerate(results):
        if i == 0 or i % 16 == 0:
            fig, ax = plt.subplots(4, 4, figsize=(15, 10), sharey=False, constrained_layout=True)
            fig.suptitle(title+f'#{i//16}', fontsize=fontsize)

        acc, thetas, rhos = results[key]
        xi = (i%16) // 4
        yi = (i%16) % 4
        ax[xi, yi].pcolor(thetas, rhos, acc)
        ax[xi, yi].title.set_text(f'Key {key}')
        ax[xi, yi].title.set_fontsize(fontsize/2)

    plt.show()


def tiled_lines(results, title='', fontsize=16):
    for i, key in enumerate(results):
        if i == 0 or i % 16 == 0:
            fig, ax = plt.subplots(4, 4, figsize=(15, 10), sharey=False, constrained_layout=True)
            fig.suptitle(title+f'#{i//16}', fontsize=fontsize)

        points, lines = results[key]
        xi = (i%16) // 4
        yi = (i%16) % 4

        x = [p[0] for p in points]
        y = [p[1] for p in points]
        ax[xi, yi].title.set_text(f'Key {key}')
        ax[xi, yi].title.set_fontsize(fontsize/2)
        ax[xi, yi].scatter(x, y, s=0.5)

        for r2, th2 in lines:
            point = (r2 * math.sin(th2), -r2 * math.cos(th2))
            slope = math.tan(th2)
            ax[xi, yi].axline(xy1=point, slope=slope, color='red')

    plt.show()
