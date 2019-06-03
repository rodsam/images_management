from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user

def required_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            # flash("You aren't allowed to visit this page！")
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return wrapper


