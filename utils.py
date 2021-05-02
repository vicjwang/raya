from collections import namedtuple
from exif import Image


Incident = namedtuple('Incident', 'lat lon created text')


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


