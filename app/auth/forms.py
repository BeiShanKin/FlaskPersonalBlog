from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(Form):
    email = StringField('邮箱', validators=[
                        Required(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[Required()])
    remember_me = BooleanField('记住密码')
    submit = SubmitField(('登陆'))


class RegisterForm(Form):
    email = StringField('邮箱', validators=[
                        Required(), Length(1, 64), Email()])
    username = StringField('用户名', validators=[Required(), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                                 'Usernames must have only letters,'
                                                                 'numbers, dots or underscores')])
    password = PasswordField('密码', validators=[Required(), EqualTo(
        'password2', message='密码不一致')])
    password2 = PasswordField('确认密码', validators=[Required()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已经注册，如果忘记密码请找回!')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经被使用!')


class ChangePasswordForm(Form):
    old_password = PasswordField('旧密码', validators=[Required()])
    password = PasswordField('新密码', validators=[Required(), EqualTo(
        'password2', message='密码不一致')])
    password2 = PasswordField('确认密码', validators=[Required()])
    submit = SubmitField('确认修改')


class SendEmailForm(Form):
    email = StringField('邮箱', validators=[Required(), Length(1, 64), Email()])
    submit = SubmitField('发送邮件')


class ResetPasswordForm(Form):
    password = PasswordField('新密码', validators=[Required(), EqualTo(
        'password2', message='密码不一致')])
    password2 = PasswordField('确认密码', validators=[Required()])
    submit = SubmitField('确认修改')
