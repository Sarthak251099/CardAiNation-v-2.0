from flask import render_template, url_for, flash, redirect, request, Blueprint
from cardination.patient.forms import RegistrationForm, LoginForm , AddRecordPat, RequestResetForm, ResetPasswordForm
from cardination.models import Patient, Record, Doctor
from cardination import db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from cardination.patient.utils import send_reset_email,worker,searching

patient = Blueprint('patient',__name__)

@patient.route("/registerPatient", methods=['GET', 'POST'])
def registerPatient():
    global boolean
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        patient = Patient(username = form.username.data,email = form.email.data,password=hashed_password,weight=form.weight.data,height=form.height.data,gender=form.gender.data,bloodgroup=form.bloodgroup.data,dob=request.form.get('DOB'))
        db.session.add(patient)
        db.session.commit()
        flash(f'Account created for {form.username.data}, Now you can login!', 'success')
        return redirect(url_for('patient.loginPatient'))
    return render_template('registerPatient.html', title='Register Patient', form=form)

@patient.route("/loginPatient", methods=['GET', 'POST'])
def loginPatient():
    if current_user.is_authenticated:
        return redirect(url_for('patient.viewRecordsPat'))
    form = LoginForm()
    if form.validate_on_submit():
        patient = Patient.query.filter_by(email = form.email.data).first()
        if patient and bcrypt.check_password_hash(patient.password,form.password.data):
            login_user(patient,remember = form.remember.data)
            next_page = request.args.get('next')
            return redirect(url_for('next_page')) if next_page else redirect(url_for('patient.viewRecordsPat'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('loginPatient.html', title='Login Patient', form=form)

@patient.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.home"))

@patient.route("/accountPat")
@login_required
def accountPat():
    image_file=url_for('static',filename='profile_pic/'+current_user.image_file)
    return render_template('accountPat.html',image_file=image_file)

@patient.route("/addRecordPat",methods=["POST","GET"])
@login_required
def addRecordPat():
    form = AddRecordPat()
    if form.validate_on_submit():
        doc = Doctor.query.filter_by(username=form.doctor.data).first()
        patientRecord = Record(date=form.date.data, symptoms = form.symptoms.data,disease=form.disease.data,prescription=form.prescription.data,patient_id=current_user.id,doctor_id=doc.id)
        db.session.add(patientRecord)
        db.session.commit()
        flash(f'Record added Successfully', 'success')
        return redirect(url_for('patient.viewRecordsPat'))
    return render_template('addRecordPat.html', title='Add Record', form=form)

@patient.route("/viewRecordsPat")
@login_required
def viewRecordsPat():
    record = Record.query.filter_by(patient_id=current_user.id).all()
    return render_template('viewRecordsPat.html',records = record)

@patient.route("/reset_password",methods=["POST","GET"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('patient.viewRecordsPat'))
    form = RequestResetForm()
    if form.validate_on_submit():
        patient = Patient.query.filter_by(email=form.email.data).first()
        send_reset_email(patient)
        flash('Email has been sent to reset your password','info')
        return redirect(url_for('patient.loginPatient'))
    return render_template('reset_request.html',title='Reset Password',form = form)

@patient.route("/reset_password/<token>",methods=["POST","GET"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('patient.viewRecordsPat'))
    patient = Patient.verify_reset_token(token)
    if patient is None:
        flash('That is an invalid or expired Token','warning')
        return redirect(url_for('patient.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        patient.password = hashed_password
        db.session.commit()
        flash(f'Your password has been updated, Now you can login!', 'success')
        return redirect(url_for('patient.loginPatient'))
    return render_template('reset_token.html', title = 'Reset Password', form = form)

@patient.route("/response")
def response():
    message = request.args.get('message')
    result = searching(message)
    if result==None:
        result = worker(message)
    return render_template("answer.html",result = result)
