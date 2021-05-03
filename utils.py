import os
import requests
import shutil
from collections import namedtuple
from exif import Image


Incident = namedtuple('Incident', 'lat lon created text image_uri')
TMP_DIR = '/tmp'


def download_image(url, filename=None):
    # Store new images in /tmp.
    if filename is None:
        filename = str(hash(url))
    filepath = os.path.join(TMP_DIR, filename)
    if os.path.isfile(filepath):
        raise RuntimeError('File already exists: {}'.format(filepath))

    resp = requests.get(url, stream=True)

    if resp.status_code != 200:
        raise RuntimeError('Invalid url: {}'.format(url))

    resp.raw.decode_content = True
    with open(filepath, 'wb') as f:
        shutil.copyfileobj(resp.raw, f)

    return filepath


def convert_dms_to_dd(d, m, s, ref):
    dd = d + m / 60 + s / 3600
    if ref in ('S', 'W'):
        dd = -dd
    return dd


def extract_latlon_from_image(image_filepath):
    with open(image_filepath, 'rb') as image_file:
        image = Image(image_file)
        if not image.has_exif:
            raise RuntimeError('{} has no exif data'.format(image_filepath))

        lat = image.gps_latitude
        lat_ref = image.gps_latitude_ref
        lon = image.gps_longitude
        lon_ref = image.gps_longitude_ref
        lat_dd = convert_dms_to_dd(*lat, lat_ref)
        lon_dd = convert_dms_to_dd(*lon, lon_ref)
        return lat_dd, lon_dd


