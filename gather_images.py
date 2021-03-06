import camera
import subprocess
import glob
import os

DESIRED_DISTANCES = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0,
                     1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]

DIST_FMT = "{0:.2f}m"
CAM_RES_DIR_FMT = "{prefix}/{cam}/{res}/{dist}"
BASENAME_FMT = "{i:03d}.jpg"


def _take_photo(camera, resolution, distance, prefix='images', wait=True):
    opts = {'prefix': prefix,
            'cam'   : camera.details.short_name,
            'res'   : "{0}x{1}".format(*resolution),
            'dist'  : DIST_FMT.format(distance)}

    cam_res_dir = CAM_RES_DIR_FMT.format(**opts)

    if not os.path.isdir(cam_res_dir):
        os.makedirs(cam_res_dir)

    existing = glob.glob(cam_res_dir + "/*.jpg")
    existing = map(lambda x: int(x[len(cam_res_dir)+1:][:3]), existing)
    i = max(existing + [-1]) + 1

    filename = cam_res_dir + '/' + BASENAME_FMT.format(i=i)

    print
    print "Taking photo:", camera.details.short_name, resolution, distance
    print "Please place a marker perpendicular to the direction the camera"
    print "is pointing in and {d} away...".format(d=distance)
    p = subprocess.Popen(['./take_photo', camera.dev_path, filename,
                          str(resolution[0]), str(resolution[1]),
                          "1" if wait else "0"],
                         stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE)
    if wait:
        raw_input('Press [ENTER] to take photo...')
        p.communicate('boo')
    p.wait()
    print "Photo", filename, "taken"


def photos_for_distance_for_all_resolutions(camera, distance, prefix='images'):
    wait = True
    for resolution in camera.details.resolutions:
        _take_photo(camera, resolution, distance, prefix=prefix, wait=wait)
        wait = False


def photos_for_all_distances_for_all_resolutions(camera, prefix='images'):
    for distance in DESIRED_DISTANCES:
        photos_for_distance_for_all_resolutions(camera, distance, prefix=prefix)


if __name__ == '__main__':
    cam = camera.choose_camera()
    if cam is None:
        print "Camera not selected, aborting"
        exit(1)

    print "Chosen", cam

    photos_for_all_distances_for_all_resolutions(cam)
