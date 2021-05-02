import mimetypes
import os
import requests
import shutil
from flask import Flask
from twilio.rest import Client as TwilioClient
from pymongo import MongoClient
from .utils import extract_latlon_from_image, Incident


app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('APP_CONFIG_FILE', silent=True)

MAPBOX_API_KEY = app.config['MAPBOX_API_KEY']
TEST_FILEPATH = '/home/vjwang45/Downloads/car-panel.jpg'
TWILIO_ACCOUNT_SID = app.config['TWILIO_ACCOUNT_SID']
TWILIO_AUTH_TOKEN = app.config['TWILIO_AUTH_TOKEN']
TWILIO_MAIN_PHONE_NUMBER = app.config['TWILIO_MAIN_PHONE_NUMBER']

TWILIO_API_DOMAIN = 'https://api.twilio.com'

LIMIT = 20
TMP_DIR = '/tmp'


twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
mongo_client = MongoClient()


@app.route('/')
def root():
    """
    Render map of all reported incidents.
    """
    # Retrieve incidents from database.
    incidents = []
    return 'hello world'


@app.route('/incidents/refresh')
def refresh_incidents():
    # Check if new messages need processing.
    messages = twilio_client.messages.list(to=TWILIO_MAIN_PHONE_NUMBER, limit=LIMIT)

    for message in messages:
        if int(message.num_media) == 0:
            continue
        created = message.date_created
        text= message.body
        for media in message.media.list():
            media_url = TWILIO_API_DOMAIN + media.uri[:-5]
            media_sid = media.sid
            ext = mimetypes.guess_extension(media.content_type)
            print('vjw media_url', media_url)

            # Store new images in /tmp.
            filepath = '{}{}'.format(os.path.join(TMP_DIR, media_sid), ext)
            if os.path.isfile(filepath):
                continue

            resp = requests.get(media_url, stream=True)

            if resp.status_code != 200:
                continue

            resp.raw.decode_content = True
            with open(filepath, 'wb') as f:
                shutil.copyfileobj(resp.raw, f)
                print('vjw wrote to {}'.format(filepath))

            try:
                lat, lon = extract_latlon_from_image(filepath)
            except RuntimeError as e:
                print('vjw skipping', e)
                continue

            incident = Incident(lat=lat, lon=lon, created=created, text=text)
            print('vjw incident', incident)
            # TODO(vjw): Save to database.

