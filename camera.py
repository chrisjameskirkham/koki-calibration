import pyudev
import re
from collections import namedtuple

CameraDetails = namedtuple('CameraDetails', ['name'])

DEV_PATH_RE = re.compile(".*video4linux/(video[0-9]+)$")
SR_CAMERAS = {(0x046d, 0x0807): CameraDetails('Logitech C500'),
              (0x046d, 0x0825): CameraDetails('Logitech C270')}

class Camera(object):
    def __init__(self, id_vendor, id_product, dev_path):
        self.id_vendor = id_vendor
        self.id_product = id_product
        self.id = (id_vendor, id_product)
        self.dev_path = dev_path
        self.details = SR_CAMERAS.get(self.id, None)


def find_cameras(just_sr_cams=True):
    context = pyudev.Context()
    devs = context.list_devices(subsystem='video4linux')
    cameras = []

    for camera in devs:
        match = DEV_PATH_RE.match(camera.device_path)
        if not match:
            continue
        dev_path = '/dev/' + match.groups()[0]
        usb_dev = camera.parent.parent
        vendor = usb_dev.attributes['idVendor']
        product = usb_dev.attributes['idProduct']
        cameras.append(Camera(int(vendor, 16), int(product, 16), dev_path))

    return filter(lambda c: not just_sr_cams or c.id in SR_CAMERAS, cameras)
