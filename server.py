from flask import Flask

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('APP_CONFIG_FILE', silent=True)

@app.route('/')
def root():
    return 'hello world'
