from datetime import datetime
from werkzeug.urls import url_parse
from flask import flash, render_template, redirect, url_for, request, g, json, current_app
from flask_login import current_user, login_required, login_user, logout_user
from app import db
from app.auth.forms import LoginForm, RegiForm
from app.models import User
from app.auth import bp
import app

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm(request.form, csrf_enabled= False)
    if form.validate_on_submit() and request.method == 'POST':
        user = User.query.filter_by(username = form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            # flash('Username or password is wrong！', 'error')
            return redirect(url_for('auth.login'))
        login_user(user)
        user.last_seen = datetime.now()
        db.session.commit()
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            if current_user.is_admin:
                next_page = url_for('admin.index')
            else:
                next_page = url_for('main.index')
        # flash('Welcome！', 'success')
        return redirect(next_page)
    return render_template('auth/login.html', form= form)

@bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))

@bp.route('/regi', methods=['GET', 'POST'])
def regi():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form  = RegiForm(request.form, csrf_enabled= False)
    if form.validate_on_submit() and request.method == 'POST':
        user = User(username= form.username.data, email=form.email.data, address= form.address.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        # flash('Congratulations, you are a registered user now!')
        return redirect(url_for('auth.login'))

    return render_template('auth/regi.html', form= form)
