from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, AnyOf
from .utils import (
    length_validation,
    lowercase_validation,
    uppercase_validation,
    digit_validation,
    special_character_validation,
)


class RegistrationForm(FlaskForm):
    email = StringField(validators=[DataRequired()])
    firstname = StringField(validators=[DataRequired()])
    lastname = StringField(validators=[DataRequired()])
    phone = StringField(validators=[DataRequired()])
    password = PasswordField(
        validators=[
            DataRequired(),
            length_validation(min=8, max=15),
            lowercase_validation,
            uppercase_validation,
            digit_validation,
            special_character_validation,
        ]
    )
    confirm_password = PasswordField(
        validators=[
            DataRequired(),
            EqualTo("password", message="Both password fields must be equal!"),
        ]
    )
    submit = SubmitField()


class LoginForm(FlaskForm):
    email = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField()
    recaptcha = StringField(validators=[DataRequired()])
