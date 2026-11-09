import matplotlib.pyplot as plt
import math



def plot_points(points):
    fig, ax = plt.subplots(1, 1, figsize=(5, 4), sharey=False)
    ax.scatter([p[0] for p in points], [p[1] for p in points])
    plt.show()

# plots lines and points
def plot_lines(ptdict, tubes, title="Detection of skewed straws"):
    for i, key in enumerate(tubes):
        lines = tubes[key]
        assert len(lines) == 7
        points = [p for p in ptdict[key]]
        assert len(points)
        if i == 0 or i % 16 == 0:
            fig, ax = plt.subplots(4, 4, figsize=(20, 15), sharey=False)
            fig.suptitle(f'{title} #{i//16}', fontsize=16)

        xi = (i%16) // 4
        yi = (i%16) % 4

        ax[xi, yi].set_ylim([0.0, 1.0])
        ax[xi, yi].set_xlim([0.0, 1.0])
        ax[xi, yi].title.set_text(f'Key {key}')
        ax[xi, yi].title.set_fontsize(10)
       
        ax[xi, yi].scatter([p[0] for p in points], [p[1] for p in points], s=0.5)

        for r2, th2 in lines:
                x = r2 * math.cos(th2)
                y = r2 * math.sin(th2)
                point = (x, y)
                slope = math.tan(th2)
                ax[xi, yi].axline(xy1=point, slope=-slope, color='red', linestyle='--')
    plt.show()
        

def plot_corrected(corrected, tubes):
    for i, pack in enumerate(corrected):
        key, points = pack
        #print(f'key {key}, points {len(points)}')
        if i == 0 or i % 16 == 0:
            fig, ax = plt.subplots(4, 4, figsize=(20, 15), sharey=False)
            fig.suptitle(f'Detection of skewed straws #{i//16}', fontsize=16)

        xi = (i%16) // 4
        yi = (i%16) % 4
        ax[xi, yi].set_ylim([0.0, 1.0])
        ax[xi, yi].set_xlim([0.0, 1.0])
        ax[xi, yi].title.set_text(f'Key {key}')
        ax[xi, yi].title.set_fontsize(10)
        ax[xi, yi].scatter([p[1] for p in points], [p[0] for p in points], s=0.5)

    for r2, th2 in tubes[key]:
        point = (r2 * math.sin(th2), r2 * math.cos(th2))
        slope = math.tan(th2)
        ax[xi, yi].axline(xy1=point, slope=-slope, color='red',
                            linestyle='--', label='xx')
    plt.show()

def plot(D, results):
    for i, key in enumerate(results):
        if i == 0 or i % 16 == 0:
            fig, ax = plt.subplots(4, 4, figsize=(20, 15), sharey=False)
            fig.suptitle(f'Detection of skewed straws #{i//16}', fontsize=16)

        peaks = results[d]
        points = getxy(key)
        xi = (i%16) // 4
        yi = (i%16) % 4

        ax[xi, yi].title.set_text(f'Key {d}')
        ax[xi, yi].title.set_fontsize(10)
        ax[xi, yi].scatter([p[0]for p in points], [p[1] for p in points], s=0.5)

    plt.show()