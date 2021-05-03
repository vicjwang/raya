import argparse
import arrow
import os
from pymongo import MongoClient
from constants import DB_NAME, TABLE_NAME

from utils import extract_latlon_from_image, Incident

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('imagefile')
    parser.add_argument('text')

    args = parser.parse_args()

    imagefile = args.imagefile
    text = args.text
    
    client = MongoClient()

    db = client[DB_NAME]

    table = db[TABLE_NAME]

    lat, lon = extract_latlon_from_image(imagefile)
    created = arrow.Arrow.fromtimestamp(os.path.getctime(imagefile)).format()
    
    incident = Incident(lat=lat, lon=lon, created=created, text=text, image_uri=imagefile)
    incident_id = table.insert_one(incident._asdict()).inserted_id
    print('Insert successful:', incident_id)
