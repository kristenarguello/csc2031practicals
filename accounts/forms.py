from flask_wtf import FlaskForm, RecaptchaField
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp

# only valid if contain letters or hyphens
NAME_REGEX = "^[a-zA-Z-]+$"

# options for uk landline numbers
THREE_CODE_DIGITS = "(02[0-9]{1}-[0-9]{8})"
FOUR_CODE_DIGITS = "((011[0-9]{1}-[0-9]{7})|(01[0-9]{1}1-[0-9]{7}))"
FIVE_CODE_DIGITS = "((01[0-9]{3}-[0-9]{5})|(01[0-9]{3}-[0-9]{6}))"


class RegistrationForm(FlaskForm):
    email = StringField(validators=[DataRequired(), Email()])
    firstname = StringField(
        validators=[
            DataRequired(),
            Regexp(
                regex=NAME_REGEX,
                message="First name must follow pattern of letters and/or hyphen.",
            ),
        ]
    )
    lastname = StringField(
        validators=[
            DataRequired(),
            Regexp(
                regex=NAME_REGEX,
                message="Last name must follow pattern of letters and/or hyphen.",
            ),
        ]
    )
    phone = StringField(
        validators=[
            DataRequired(),
            Regexp(
                regex=f"^({THREE_CODE_DIGITS}|{FOUR_CODE_DIGITS}|{FIVE_CODE_DIGITS})$",
                message="Phone number must be a valid UK landline number.",
            ),
        ]
    )
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
                regex=".*[$&+,:;=?@#|'<>.-^*()%!]",
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
    mfa_key = StringField(validators=[DataRequired()])
    submit = SubmitField()
    recaptcha = RecaptchaField()
