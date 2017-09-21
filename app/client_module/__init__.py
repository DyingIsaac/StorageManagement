from flask import Blueprint

client = Blueprint('client', __name__, url_prefix='/clients')

from . import views