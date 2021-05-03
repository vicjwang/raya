import argparse
import arrow
import os
import requests
import shutil
from pymongo import MongoClient
from constants import DB_NAME, TABLE_NAME

from utils import extract_latlon_from_image, Incident, download_image

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--imagefile')
    parser.add_argument('--url')
    parser.add_argument('--text', default='')

    args = parser.parse_args()

    imagefile = args.imagefile
    url = args.url
    text = args.text

    assert not imagefile or not url, 'Cannot have both imagefile and url parameters.'
    assert imagefile or url, 'Please provide either imagefile or url parameter'

    image_uri = None
    if url:
        imagefile = download_image(url)
        image_uri = url
    elif imagefile:
        basename = os.path.basename(imagefile)
        filepath = './static/{}'.format(basename)
        shutil.copyfile(imagefile, filepath)
        image_uri = filepath
    lat, lon = extract_latlon_from_image(imagefile)
    created = arrow.Arrow.fromtimestamp(os.path.getctime(imagefile)).format()
    incident = Incident(lat=lat, lon=lon, created=created, text=text, image_uri=image_uri)

    client = MongoClient()
    db = client[DB_NAME]
    table = db[TABLE_NAME]

    incident_id = table.insert_one(incident._asdict()).inserted_id
    print('Insert successful:', incident_id)
