# coding: utf-8
from flask import render_template, url_for, redirect, flash, request
from . import auth
from flask_login import login_required, current_user, logout_user, login_user
from .forms import LoginForm, RegisterForm
from ..models import User
from .. import db


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('输入的用户名或密码有误')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    flash('登出成功')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        print(form)
        user = User(username=form.username.data,
                    email=form.email.data, password=form.password.data)
        db.session.add(user)
        flash('注册成功，可以登录了')
        return redirect(url_for('.login'))
    return render_template('auth/register.html', form=form)
