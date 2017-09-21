from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user
from . import auth
from ..models import Client, Employee
from .forms import LoginForm, RegistrationForm


@auth.route('/login/', methods=['GET', 'POST'])
@auth.route('/<any("client-"):user_type>login/', methods=['GET', 'POST'])
def login(user_type=None):
    form = LoginForm()
    if form.validate_on_submit():
        where_statement = 'email="{}"'.format(form.email.data)
        user = Client.query.filter_by(where_statement).first() if user_type else Employee.query.filter_by(where_statement).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or (url_for('client.index', nickname=user.nickname) if user_type
                                                         else url_for('manage.index', nickname=user.nickname)))
        flash('用户名不存在或密码错误.')
    return render_template('auth/login.html', page_title='登录', form=form, user_type='用户' if user_type else '员工')


@auth.route('/client-register/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Client(addr=form.addr.data, name=form.name.data, email=form.email.data, nickname=form.username.data, pw=None)
        user.password = form.password.data
        user.insert_db()
        flash('注册成功')
        return redirect(url_for('auth.login', user_type='client-'))
    return render_template('auth/register.html', form=form)


@auth.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('账户已登出')
    return redirect(url_for('main.index'))
