from flask import Flask
from flask_mysqldb import MySQL
import os, sys, time
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from jinja2 import Environment, utils
from flask_ipban import IpBan

app = Flask(__name__)


app.config['SECRET_KEY'] = '\x83\xe1\xba%j\x0b\xe5Q\xdeiG\xde\\\xb1\x94\xe4\x0e\x1dk\x99\x1a\xda\xe8x'
app.config['MYSQL_HOST'] = 'db'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_USER'] = 'challenge'
app.config['MYSQL_PASSWORD'] = 'challengepass'
app.config['MYSQL_DB'] = 'challengedb'
app.config['MAX_CONTENT_PATH'] = 102400

ip_ban = IpBan(ban_seconds=1800, ban_count=2)
ip_ban.init_app(app)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per day", "30 per hour"]
)

mysql = MySQL(app)
current_user = None


from model import *
from views import * 

if __name__ == '__main__':
    ### enabled debug
    # app.run(host='127.0.0.1', debug=True)

    ### # for mac you need a workaround and probably need to run it on 0.0.0.0
    ### # https://runnable.com/docker/python/docker-compose-with-flask-apps
    app.run(host='0.0.0.0', debug=False)
