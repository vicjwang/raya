import mimetypes
from flask import Flask, render_template
from twilio.rest import Client as TwilioClient
from pymongo import MongoClient
from .utils import extract_latlon_from_image, Incident, download_image
from .constants import DB_NAME, TABLE_NAME


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


twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
mongo_client = MongoClient()
db = mongo_client[DB_NAME]
table = db[TABLE_NAME]


@app.route('/')
def root():
    """
    Render map of all reported incidents.
    """
    # Retrieve incidents from database.
    incidents = list(table.find())
    for incident in incidents:
        del incident['_id']

    return render_template(
      'root.html',
      MAPBOX_API_KEY=MAPBOX_API_KEY,
      incidents=incidents
    )


@app.route('/twilio/messages')
def twilio_messages():
    messages = twilio_client.messages.list(to=TWILIO_MAIN_PHONE_NUMBER, limit=LIMIT)
    html = '<div>'

    for message in messages:
        if int(message.num_media) == 0:
            continue
        created = message.date_created
        text= message.body
        for media in message.media.list():
            media_url = TWILIO_API_DOMAIN + media.uri[:-5]
            html += '<div>' + media_url + '</div>'
    html += '</div>'
    return html
    


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
            filename = media_sid + ext
            filepath = download_image(media_url, filename)

            try:
                lat, lon = extract_latlon_from_image(filepath)
            except RuntimeError as e:
                continue

            incident = Incident(lat=lat, lon=lon, created=created, text=text, image_uri=media_url)
            # TODO(vjw): Save to database.

