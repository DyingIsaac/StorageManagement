from functools import wraps
from flask import abort
from flask_login import current_user, login_required
from .models import Client, Employee


def permission_required(cls):
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not isinstance(current_user._get_current_object(), cls):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def client_required(f):
    return permission_required(Client)(f)


def employee_required(f):
    return permission_required(Employee)(f)


@employee_required
def su_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.isSU:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
