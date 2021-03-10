import math
import numpy as np
import matplotlib.pyplot as plt

maps = [
    {'name': 'Karakin',
     'map_size': 2,
     'num_players': 64,
     'bgimg': 'karakin_map.png',
     'phases': [{'delay': 60, 'wait': 120, 'move': 120, 'shrink': 0.55},
                {'delay':  0, 'wait': 120, 'move':  90, 'shrink': 0.70},
                {'delay':  0, 'wait':  90, 'move':  90, 'shrink': 0.60},
                {'delay':  0, 'wait':  60, 'move':  60, 'shrink': 0.60},
                {'delay':  0, 'wait':  60, 'move':  60, 'shrink': 0.60},
                {'delay':  0, 'wait':  30, 'move':  60, 'shrink': 0.50},
                {'delay':  0, 'wait':  30, 'move':  30, 'shrink': 0.50},
                {'delay':  0, 'wait':  30, 'move':  30, 'shrink': 0.50},
                {'delay':  0, 'wait':  30, 'move':  30, 'shrink': 0.001},
                ]},
    {'name': 'Erangel',
     'map_size': 8,
     'num_players': 100,
     'bgimg': 'erangel_map.jpg',
     'phases': [{'delay': 120, 'wait': 270, 'move': 300, 'shrink': 0.35},
                {'delay':   0, 'wait': 180, 'move': 120, 'shrink': 0.60},
                {'delay':   0, 'wait': 130, 'move':  90, 'shrink': 0.55},
                {'delay':   0, 'wait': 120, 'move':  60, 'shrink': 0.55},
                {'delay':   0, 'wait': 100, 'move':  60, 'shrink': 0.50},
                {'delay':   0, 'wait':  90, 'move':  30, 'shrink': 0.50},
                {'delay':   0, 'wait':  70, 'move':  30, 'shrink': 0.50},
                {'delay':   0, 'wait':  60, 'move':  30, 'shrink': 0.50},
                {'delay':  30, 'wait':  30, 'move':  30, 'shrink': 0.001},
                ]},
]

# delay: Set the delay for when the next safe zone will appear.
# wait: This setting controls the time until the blue zone starts moving once the next circle has been shown.
# move: Adjust how fast the blue zone moves during each phase.
# shrink: This number controls how small each safe zone will be compared to the previous safe zone. (0.1 will make it 10% the size of the previous safe zone).

# map_size is defined as the length of the sides of the square map in km (l), the corresponding circle diameter is sqrt(2*(l*l)) (d), blue zone radius is d/2 (r),  blue zone area is pi*r*r

def blue_zone_diameter(map_size):
    return math.sqrt(2*map_size**2)


def blue_zone_diameter(map_size):
    return math.sqrt(2*map_size**2)


def blue_zone_radius(map_size):
    return blue_zone_diameter(map_size) / 2


def blue_zone_area(map_size):
    return math.pi * blue_zone_radius(map_size)**2


def total_time(map):
    return sum(phase['delay'] + phase['wait'] + phase['move'] for phase in map['phases'])


def  map_size_for_blue_zone_area(area):
    """
    >>>  map_size_for_blue_zone_area(blue_zone_area(1))
    1.0
    >>>  map_size_for_blue_zone_area(blue_zone_area(100.0))
    100.0
    >>> round(map_size_for_blue_zone_area(blue_zone_area(1337.6)), 1)
    1337.6
    """
    return math.sqrt((((math.sqrt(area / math.pi)) * 2)**2)/2)


def calculate_required_shrink_phase1(map_name, num_players):
    """
    Calculate shrink for existing first phase at start so play area per player will be the same after first phase (with delay/wait at 0 and move at sum of original delay/wait/move).

    >>> calculate_required_shrink_phase1('Karakin', 10)
    0.2174065891365761
    >>> calculate_required_shrink_phase1('Erangel', 10)
    0.11067971810589328
    """
    m = next(m for m in maps if m['name'] == map_name)
    first_map_size = m['map_size'] * m['phases'][0]['shrink']
    return calculate_required_shrink(m, num_players, first_map_size)


def calculate_required_shrink_phase0(map_name, num_players):
    """
    Calculate shrink for prepended phase at start so play area per player will be the same (with prepended phase's delay/wait/move at 0).

    >>> calculate_required_shrink_phase0('Karakin', 10)
    0.39528470752104744
    """
    m = next(m for m in maps if m['name'] == map_name)
    first_map_size = m['map_size']
    return calculate_required_shrink(m, num_players, first_map_size)

def calculate_required_shrink(m, num_players, first_map_size):
    first_blue_zone_area = blue_zone_area(first_map_size)

    required_blue_zone_area = first_blue_zone_area / m['num_players'] * num_players

    required_map_size = map_size_for_blue_zone_area(required_blue_zone_area)

    required_shrink = required_map_size / m['map_size']

    return required_shrink


def create_map_size_method_for_map(m):
    times = []
    map_sizes = []
    time = 0
    map_size = m['map_size']
    times.append(time)
    map_sizes.append(map_size)
    for phase in m['phases']:
        time += phase['delay'] + phase['wait']
        times.append(time)
        map_sizes.append(map_size)

        time += phase['move']
        map_size *= phase['shrink']
        times.append(time)
        map_sizes.append(map_size)

    def map_size(time):
        return np.interp(time, times, map_sizes)
    return map_size


if __name__ == '__main__':
    show_maps = True
    show_area_per_player = True

    nrow = 2 if show_maps and show_area_per_player else 1
    ncol = len(maps) if show_maps else 1
    fig, axes = plt.subplots(nrow, ncol, sharex=False, squeeze=False,
                             gridspec_kw=dict(wspace=0.15, hspace=0.15),
                             figsize=(ncol + 1, nrow + 1))

    # create X-axis
    max_time = max(total_time(m) for m in maps)
    X = np.arange(0, max_time, 0.05)

    if show_maps:
        for i, m in enumerate(maps):
            ax = axes[0][i]

            map_size = create_map_size_method_for_map(m)

            y = np.array([blue_zone_radius(x) for x in map_size(X)])

            ax.plot(X, y, c='tab:blue')
            ax.plot(X, -y, c='tab:blue')

            ax.fill_between(X, y, m['map_size']/2, color='tab:blue', alpha=0.5)
            ax.fill_between(X, -y, -m['map_size']/2, color='tab:blue', alpha=0.5)

            img = plt.imread(m['bgimg'])
            ax.imshow(img, extent=(0, max_time, -
                                   m['map_size']/2, m['map_size']/2), aspect='auto')

            ax.set_xlabel("time (s)")
            ax.set_ylabel("blue zone radius (km)")
            ax.set_title(
                f"Blue zone radius {m['name']} {m['num_players']}p")

    if show_area_per_player:

        ax = axes[1][0] if show_maps else axes[0][0]

        for m in maps:
            map_size = create_map_size_method_for_map(m)

            y = np.array([(blue_zone_area(x)/m['num_players'])
                          * 1_000_000 for x in map_size(X)])

            ax.semilogy(
                X, y, label=f"{m['name']} {m['num_players']}p", alpha=0.5)

        ax.grid()
        ax.set_xlabel("time (s)")
        ax.set_ylabel("area per player (m²)")
        ax.set_xlim(left=0)
        ax.set_ylim(bottom=1)
        ax.legend()
        ax.set_title('Blue zone area per player')

        # turn off other, empty graphs
        for i in range(1, ncol):
            axes[1][i].axis('off')

    # fig.tight_layout() # don't use this, because we use gridspec
    plt.show()
