from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import DataRequired ,Length

class Login(FlaskForm):
    rollno = StringField("Roll Number",validators=[DataRequired()])
    password = PasswordField("password",validators=[DataRequired()] )
    submit = SubmitField("Login")

class Logout(FlaskForm):
        submit = SubmitField("Login")