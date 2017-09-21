from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Length, Email, Regexp, EqualTo, ValidationError
from ..models import Client


class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[InputRequired(), Length(1,30), Email()])
    password = PasswordField('密码', validators=[InputRequired()])
    remember_me = BooleanField('保持登陆')
    submit = SubmitField('登陆')


class RegistrationForm(FlaskForm):
    email = StringField('邮箱', validators=[InputRequired(), Length(1, 30), Email()])
    username = StringField('昵称', validators=[
        InputRequired(), Length(1, 10), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                               '昵称只能使用 字母 数字 . 和 _')])
    password = PasswordField('密码', validators=[InputRequired(), Length(6, 15), EqualTo('password2', message='密码不匹配')])
    password2 = PasswordField('确认密码', validators=[InputRequired()])
    name = StringField('姓名', validators=[InputRequired(), Length(1, 30)])
    addr = StringField('地址', validators=[InputRequired(), Length(1, 30)])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if Client.query.filter_by('email="{}"'.format(field.data)).first():
            raise ValidationError('邮箱已经注册')

    def validate_username(self, field):
        if Client.query.filter_by('nickname="{}"'.format(field.data)).first():
            raise ValidationError("昵称已被占用")
