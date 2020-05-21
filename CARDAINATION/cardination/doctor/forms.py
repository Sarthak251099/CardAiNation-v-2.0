from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from cardination.models import Patient, Doctor

class RegisterDoc(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    specialization = StringField('Specialization')
    degree = StringField('Degree')
    phonenumber = StringField('Phone Number')
    address = StringField('Address')
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        doctor = Doctor.query.filter_by(username = username.data).first()
        if doctor:
            raise ValidationError('That username is taken. Please choose another username')
    def validate_email(self, email):
        doctor = Doctor.query.filter_by(email = email.data).first()
        if doctor:
            raise ValidationError('That email is taken. Please choose another username')

class AddRecordDoc(FlaskForm):
    patient = StringField('Patient username',validators=[DataRequired()])
    date = StringField('Date')
    symptoms = StringField('Symptoms')
    disease = StringField('Disease')
    prescription = StringField('Prescription')
    additional_info = TextAreaField('Additonal Information')
    submit = SubmitField('ADD RECORD')

    def validate_patient(self, patient):
        pat = Patient.query.filter_by(username = patient.data).first()
        if not pat:
            raise ValidationError('Patient account with this username does not exist. Create patient account first')
 