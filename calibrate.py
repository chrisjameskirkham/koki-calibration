from gather_images import CAM_RES_DIR_FMT, BASENAME_FMT
import subprocess
import glob
import sys
import re
import os
from scipy import optimize

DIST_DIR_RE = re.compile(".*([0-9]+\.[0-9]+m)/?$")
RES_DIR_RE = re.compile(".*/([0-9]+)x([0-9]+)/?$")

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
        perc_error = (actual-expected)/expected
        return perc_error ** 2

    return optimize.golden(error_func, brack=(250.0, 750.0), tol=0.001)


def bests_for_res_dir(directory, marker_width):
    distances = glob.glob(directory + '/*')
    bests = {}
    for distance in distances:
        d = DIST_DIR_RE.match(distance).groups()[0]
        bests[d] = best_for_dist_dir(distance, marker_width)
    return bests


def bests_for_cam_dir(directory, marker_width):
    resolutions = glob.glob(directory + '/*')
    bests = {}
    for resolution in resolutions:
        r = RES_DIR_RE.match(resolution).groups()
        bests[(int(r[0]), int(r[1]))] = bests_for_res_dir(resolution, marker_width)
    return bests


def bests_for_cam(short_name, marker_width, prefix='images'):
    cam_dir = prefix + '/' + short_name
    if not os.path.isdir(cam_dir):
        return None
    return bests_for_cam_dir(cam_dir, marker_width)



if __name__ == '__main__':
    print bests_for_cam('C270', 0.78)