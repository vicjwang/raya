. ~/.bashrc
export FLASK_APP=server.py
export FLASK_DEBUG=1
export APP_CONFIG_FILE=settings.py
. ~/code/envs/raya/bin/activate
flask run
