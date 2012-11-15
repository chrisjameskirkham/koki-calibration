import camera
import subprocess
import glob
import os

DESIRED_DISTANCES = ["{0:.2f}m".format(x) for x in
                     (0.3, 0.4, 0.5, 0.75, 1.0, 1.5)]

CAM_RES_DIR_FMT = "{prefix}/{cam}/{res}/{dist}"
BASENAME_FMT = "{i:03d}.jpg"


def _take_photo(camera, resolution, distance, prefix='images'):
    opts = {'prefix': prefix,
            'cam'   : camera.details.short_name,
            'res'   : "{0}x{1}".format(*resolution),
            'dist'  : distance}

    cam_res_dir = CAM_RES_DIR_FMT.format(**opts)

    if not os.path.isdir(cam_res_dir):
        os.makedirs(cam_res_dir)

    existing = glob.glob(cam_res_dir + "/*.jpg")
    existing = map(lambda x: int(x[len(cam_res_dir)+1:][:3]), existing)
    i = max(existing + [-1]) + 1

    filename = cam_res_dir + '/' + BASENAME_FMT.format(i=i)

    p = subprocess.call(['./take_photo', camera.dev_path, filename,
                         str(resolution[0]), str(resolution[1])])


def photos_for_all_distances(camera, resolution, prefix='images'):
    for distance in DESIRED_DISTANCES:
        _take_photo(camera, resolution, distance, prefix=prefix)


def photos_for_all_resolutions(camera, prefix='images'):
    for resolution in camera.details.resolutions:
        photos_for_all_distances(camera, resolution, prefix=prefix)




if __name__ == '__main__':
    cam = camera.choose_camera()
    if cam is None:
        print "Camera not selected, aborting"
        exit(1)

    print "Chosen", cam

