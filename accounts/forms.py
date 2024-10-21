from flask_wtf import FlaskForm, RecaptchaField
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Regexp


class RegistrationForm(FlaskForm):
    email = StringField(validators=[DataRequired()])
    firstname = StringField(validators=[DataRequired()])
    lastname = StringField(validators=[DataRequired()])
    phone = StringField(validators=[DataRequired()])
    password = PasswordField(
        validators=[
            DataRequired(),
            Length(
                min=8, max=15, message="Password must be between 8 and 15 characters."
            ),
            Regexp(
                regex=".*[A-Z]", flags=0, message="Password must contain an uppercase."
            ),
            Regexp(
                regex=".*[a-z]", flags=0, message="Password must contain a lowercase."
            ),
            Regexp(regex=".*[0-9]", flags=0, message="Password must contain a digit."),
            Regexp(
                regex=".*[@#$%^&+=]",
                flags=0,
                message="Password must contain a special character.",
            ),
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
    recaptcha = RecaptchaField()
