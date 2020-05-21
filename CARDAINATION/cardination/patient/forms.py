from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from cardination.models import Patient, Doctor

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    weight = StringField('Weight')
    height = StringField('Height')
    gender = StringField('Gender',validators=[ Length(min=0,max=1)])
    bloodgroup = StringField('Blood Group')
    DOB = StringField('Date of Birth')
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        patient = Patient.query.filter_by(username = username.data).first()
        if patient:
            raise ValidationError('That username is taken. Please choose another username')
    def validate_email(self, email):
        patient = Patient.query.filter_by(email = email.data).first()
        if patient:
            raise ValidationError('That email is taken. Please choose another username')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class AddRecordPat(FlaskForm):
    doctor = StringField('Doctor username',validators=[DataRequired()])
    date = StringField('Date')
    symptoms = StringField('Symptoms')
    disease = StringField('Disease')
    prescription = StringField('Prescription')
    additional_info = TextAreaField('Additonal Information')
    submit = SubmitField('ADD RECORD')
    
    def validate_doctor(self, doctor):
        doc = Doctor.query.filter_by(username = doctor.data).first()
        if not doc:
            raise ValidationError('Doctor account with this username does not exist. Create doctor account first')
    
class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        patient = Patient.query.filter_by(email = email.data).first()
        if patient is None:
            raise ValidationError('There is no account with that email. You need to register first')
    
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')