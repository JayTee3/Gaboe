

from flask import redirect, render_template, request, session
from functools import wraps



def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
            if session.get("teacher_id") is None:
                return redirect("/")
            return f(*args, **kwargs)
    return decorated_function

def login_required_student(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
            if session.get("student_id") is None:
                return redirect("/home")
            return f(*args, **kwargs)
    return decorated_function