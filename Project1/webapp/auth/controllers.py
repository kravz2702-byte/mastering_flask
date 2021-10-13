from .forms import LoginForm, RegisterForm, OpenIDForm
from .models import db, User
from flask import render_template, Blueprint, redirect, url_for, flash
from flask_login import login_user, logout_user

auth_blueprint = Blueprint(
    'auth',
    __name__,
    template_folder='../templates/auth',
    url_prefix='login'

)

@auth_blueprint.route('/login', methods=['POST', 'GET'])
@oid.loginhandler
def login():
    form = LoginForm()
    openid_form = OpenIDForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).one()
        login_user(user, remember=form.remember.data)
        flash("You have been logged in", category='success')
        return redirect(url_for('main.index'))

    return render_template('login.html', form=form, openid_form=openid_form)

@auth_blueprint.route('/logout', methods=['GET', 'POST'])
def logout():
    login_user()
    flash("You have been loged out", category="success")
    return redirect(url_for('main.index'))

@auth_blueprint('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm
    if form.validate_on_submit():
        new_user = User()
        new_user.username = form.username.data 
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        db.session.commit()
        flash('Your user has been created', category='success')
        return redirect(url_for('.login'))
    return render_template('register.html', form=form)