from flask import render_template
from flask_login import login_required
from ..decorators import client_required

from . import client


@client.route('/<nickname>/')
@client_required
def index(nickname):
    return render_template('user.html', nickname=nickname)

