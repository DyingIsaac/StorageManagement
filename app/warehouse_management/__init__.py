from flask import Blueprint

manage = Blueprint('manage', __name__, url_prefix='/manage')

from . import views
