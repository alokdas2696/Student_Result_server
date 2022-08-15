from flask import Blueprint, request, render_template, session, redirect, make_response
from .models import Student
import os
import smtplib
import random
import pdfkit


main = Blueprint('main', __name__)


def generate_otp():
    return random.randint(1111, 9999)


@main.route('/', methods=['GET'])
def home():
    session.pop('username', None)
    return render_template("email.html")


# ----------Send OTP ---------------
def send_otp(email, gen_otp):
    # generated otp will be store in x
    gen_otp = generate_otp()
    # Storing otp in session
    session['response'] = str(gen_otp)
    # sending otp to registered email-id respective to roll number
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('sturesultserver@gmail.com', os.environ.get('PASS'))
        subject = 'OTP FROM RESULT SERVER'
        body = gen_otp
        msg = f'Subject:{subject}\n\nDear Student \n \n ' \
              f'The one-time password (OTP) for validating your email id is :-{body} ' \
              f'and do not share this OTP with anyone.'
        smtp.sendmail('sturesultserver@gmail.com', email, msg)


# ---------- Resend OTP ---------------
@main.route("/resendotp", methods=['GET', 'POST'])
def resend():
    if request.method == 'POST':
        if 'email' in session:
            email_db = session['email'][0]
            gen_otp = generate_otp()  # generate otp
            send_otp(email_db, gen_otp)  # resend otp
            sid = session['email'][1]
            return render_template("verify.html", sid=sid)
    return redirect('/')


# ----------------Verify---------------------
@main.route("/verify", methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        sid = request.form['rollno']
        stu_id = Student.query.get(sid)
        if stu_id is None:
            return render_template('email.html', msg="Please Enter Valid Roll NO")

        email_db = stu_id.email
        session['email'] = (email_db, sid)
        gen_otp = generate_otp()
        send_otp(email_db, gen_otp)

        return render_template("verify.html", sid=sid)
    return render_template("email.html")


@main.route('/validate/<int:sid>', methods=['GET', 'POST'])
def validate(sid):
    if request.method == 'POST':
        data = Student.query.get(sid)
        email_db = data.email
        user_otp = request.form['otp']
        if 'response' in session:
            s = session['response']
            session.pop('response', None)
            if s == str(user_otp):

                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login('sturesultserver@gmail.com', os.environ.get('PASS'))
                    subject = 'Result'
                    body = (str(data.name) + "\n Email: " + str(data.email) + "\n Math Marks: " + str(data.mtmarks) +
                            "\n Science Marks: " + str(data.scmarks) + "\n Computer Marks: " + str(data.csmarks) +
                            "\n Total Marks:" + str(data.csmarks + data.mtmarks + data.scmarks) + "\n Percentage: " +
                            str(round(((data.csmarks + data.mtmarks + data.scmarks)/300)*100)))

                    msg = f'Subject:{subject}\n\n{body}'
                    smtp.sendmail('sturesultserver@gmail.com', email_db, msg)
                return render_template('result.html', data=data, sid=sid,
                                       msg="Result has been Send to your given respected Email Id")
        return render_template("email.html", msg="Wrong OTP!........Please Login Again")


@main.route('/download/<int:sid>', methods=['GET', 'POST'])
def download(sid):
    data = Student.query.get(sid)
    rendered = render_template('result.html', data=data, msg="Result has been Send to your given respected Email Id")
    path_wkhtmltopdf = b"C:\Program Files\wkhtmltopdf\\bin\wkhtmltopdf.exe"
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    pdf = pdfkit.from_string(rendered, False, configuration=config)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=MyResult.pdf'
    return response
