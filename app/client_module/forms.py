from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import InputRequired, EqualTo


class ModifyPasswordForm(FlaskForm):
    password = PasswordField('新密码', validators=[InputRequired(), EqualTo('password2', '密码不匹配')])
    password2 = PasswordField('确认密码', validators=[InputRequired()])

    submit = SubmitField('确认修改')
