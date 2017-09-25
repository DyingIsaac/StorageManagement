from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Length, Email, Regexp, EqualTo, ValidationError
from ..models import Employee
from datetime import date


class AddEmployeeForm(FlaskForm):
    name = StringField('姓名', validators=[InputRequired()])
    sex = StringField('性别', validators=[InputRequired(), Length(1)], render_kw={'placeholder':'F/M'})
    email = StringField('邮件地址', validators=[InputRequired(), Email()], )
    birthday = StringField('生日', validators=[InputRequired()], render_kw={'placeholder':'####-##-##'})
    password = PasswordField('密码', validators=[InputRequired(), Length(6, 15), EqualTo('password2', message='密码不匹配')])
    password2 = PasswordField('确认密码', validators=[InputRequired()])

    submit = SubmitField('确认添加')

    def validate_email(self, field):
        if Employee.query.filter_by('email="{}"'.format(field.data)).first():
            raise ValidationError('邮箱已经注册')

    def validate_username(self, field):
        if Employee.query.filter_by('nickname="{}"'.format(field.data)).first():
            raise ValidationError('昵称已被占用')

    def validate_birthday(self, field):
        if len(field.data) != 10:
            raise ValidationError('请使用正确的格式：####-##-##')
        try:
            year = int(field.data[:4])
            month = int(field.data[5:7])
            day = int(field.data[8:])
        except ValueError:
            raise ValidationError('只能使用数字')
        try:
            if date(year, month, day) > date.today():
                raise ValidationError('大于今天的日期')
        except ValueError:
            raise ValidationError('日期不正确')

    def validate_sex(self, field):
        if field.data not in 'FM':
            raise ValidationError('只能为F(男)或M(女)')


class AddWarehouseForm(FlaskForm):
    name = StringField('名称', validators=[InputRequired(), Length(1, 15)])
    addr = StringField('地址', validators=[InputRequired(), Length(1, 30)])

    submit = SubmitField('确认添加')


class ModifyPasswordForm(FlaskForm):
    password = PasswordField('新密码', validators=[InputRequired(), EqualTo('password2', '密码不匹配')])
    password2 = PasswordField('确认密码', validators=[InputRequired()])

    submit = SubmitField('确认修改')
