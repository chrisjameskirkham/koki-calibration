from gather_images import CAM_RES_DIR_FMT, BASENAME_FMT
import subprocess
import glob
import sys
import re
import os
import scipy
import pickle
from scipy import optimize

DIST_DIR_RE = re.compile(".*([0-9]+\.[0-9]+m)/?$")
RES_DIR_RE = re.compile(".*/([0-9]+)x([0-9]+)/?$")

POLYFIT_DEGREE = 1

class NoMarkerFoundError(Exception):
    pass

_ignore_cache = set()

def dist_at_focal_length(filename, focal_length, marker_width):
    global _ignore_cache
    if filename in _ignore_cache:
        return None

    try:
        return float(subprocess.check_output(['./dist_at_focal_length',
                                              filename,
                                              str(focal_length),
                                              str(marker_width)]))
    except subprocess.CalledProcessError:
        _ignore_cache.add(filename)
        print >>sys.stderr, "Skipping", filename, "-- dist_at_focal_length failed"
        return None


def average_for_dist_dir(directory, focal_length, marker_width):
    def dist_curry(filename):
        return dist_at_focal_length(filename, focal_length, marker_width)

    images = glob.glob(directory + '/*.jpg')
    images = filter(lambda x: x is not None, map(dist_curry, images))
    if len(images) == 0:
        return None
    return sum(images) / len(images)


def best_for_dist_dir(directory, marker_width):
    expected = float(DIST_DIR_RE.match(directory).groups()[0][:-1])

    def error_func(focal_length):
        actual = average_for_dist_dir(directory, focal_length, marker_width)
        if actual is None:
            raise NoMarkerFoundError()
        perc_error = (actual-expected)/expected
        return perc_error ** 2

    # Golden section search sometimes returns negative values due
    # to the way it searches.  This is not a problem as a negative
    # focal length will yield the same result as it's positive
    # counterpart.
    return abs(optimize.golden(error_func, brack=(250.0, 750.0)))


def bests_for_res_dir(directory, marker_width):
    distances = glob.glob(directory + '/*')
    bests = {}
    for distance in distances:
        d = DIST_DIR_RE.match(distance).groups()[0]
        try:
            bests[d] = best_for_dist_dir(distance, marker_width)
        except NoMarkerFoundError:
            bests[d] = None
            print >>sys.stderr, "No marker found for", distance, "in", directory
    return bests


def bests_for_cam_dir(directory, marker_width):
    resolutions = glob.glob(directory + '/*')
    bests = {}
    for resolution in resolutions:
        match = RES_DIR_RE.match(resolution)
        if match is None:
            continue
        r = match.groups()
        bests[(int(r[0]), int(r[1]))] = bests_for_res_dir(resolution, marker_width)
    return bests


def bests_for_cam(short_name, marker_width, prefix='images'):
    cam_dir = prefix + '/' + short_name
    if not os.path.isdir(cam_dir):
        return None
    return bests_for_cam_dir(cam_dir, marker_width)


def save_bests(bests, short_name, prefix='images'):
    with open(prefix + '/' + short_name + '/bests.pickle', 'w') as f:
        pickle.dump(bests, f)


def load_bests(short_name, prefix='images'):
    f = open(prefix + '/' + short_name + '/bests.pickle')
    bests = pickle.load(f)
    f.close()
    return bests


def polyfits_for_bests(bests, degree=POLYFIT_DEGREE):
    def filter_outliers(items, chop_pc=0.2, min_points=4):
        x, y = zip(*items)
        y_median = scipy.median(y)
        y_std = scipy.std(y)
        deltas = []
        for _x, _y in items:
            deltas.append((_x, _y, abs(_y-y_median)))
        deltas = sorted(deltas, key=lambda x: x[2], reverse=True)
        n = min(len(items)-min_points, int(chop_pc*len(items)))
        new_len = len(items) - n
        deltas = deltas[n/2:][:new_len]
        return map(lambda x: (x[0], x[1]), deltas)

    fits = {}
    for res in bests:
        items = filter(lambda x: x[1] is not None, bests[res].items())
        items = map(lambda x: (float(x[0][:-1]), x[1]), items)
        items = filter_outliers(items, chop_pc=0.4)
        x, y = zip(*items)
        fits[res] = scipy.polyfit(x, y, degree)
    return fits


def best_focal_length_for_res(fits, resolution, distance_hint=0.5):
    return scipy.polyval(fits[resolution], distance_hint)

if __name__ == '__main__':
    print bests_for_cam('C270', 0.78)
