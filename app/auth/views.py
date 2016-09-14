# coding: utf-8
from flask import render_template, url_for, redirect, flash, request
from . import auth
from flask_login import login_required, current_user, logout_user, login_user
from .forms import LoginForm, RegisterForm, ChangePasswordForm, SendEmailForm, ResetPasswordForm
from ..models import User
from .. import db
from ..email import send_email


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
        user = User(username=form.username.data,
                    email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('注册成功，可以登录了')
        return redirect(url_for('.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('你已经通过了验证，非常感谢！')
    else:
        flash('验证链接无效或过期，请重新申请发送验证链接。')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, '账户验证',
               'auth/email/confirm', user=current_user, token=token)
    flash('一个新的验证邮件已经发送到了你的邮箱中，请查收。')
    return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated and not current_user.confirmed and request.endpoint[:5] != 'auth.' and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html', current_user=current_user)


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('密码修改成功')
            return redirect(url_for('main.index'))
        else:
            flash('旧密码错误')
    return render_template('auth/change_password.html', form=form)


@auth.route('/password-reset-request', methods=['GET', 'POST'])
def password_reset_request():
    form = SendEmailForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_password_token()
            send_email(form.email.data, '重设密码',
                       'auth/email/reset_password', user=user, token=token)
            flash('一个新的验证邮件已经发送到了你的邮箱中，请查收。')
            return redirect(url_for('main.index'))
        else:
            flash('邮箱未注册，请检查输入邮箱是否正确')
    return render_template('auth/send_email.html', form=form)


@auth.route('/password-reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    print('到这一步了吗？')
    form = ResetPasswordForm()
    result, user = User.reset_password(token)
    if form.validate_on_submit():
        user.password = form.password.data
        db.session.add(user)
        flash('密码重设成功')
        login_user(user)
        return redirect(url_for('main.index'))
    else:
        if result:
            flash('请重设密码')
        else:
            flash('无效链接或链接超时')
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/password-reset')
def resend_password_reset():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        return redirect(url_for('main.index'))
