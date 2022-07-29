from flask import Blueprint,request,render_template,session,redirect,flash, make_response
from .models import Student
from .extensions import db
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


def send_otp(email, x):
    x = generate_otp()
    session['response'] = str(x)  # Storing otp in session
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('sturesultserver@gmail.com', 'nwcknlephjurfrgx')
        subject = 'OTP FROM RESULT SERVER'
        body = x
        msg = f'Subject:{subject}\n\nDear Student \n \n ' \
              f'The one-time password (OTP) for validating your email id is :-{body} ' \
              f'and do not share this OTP with anyone.'
        smtp.sendmail('sturesultserver@gmail.com', email, msg)


@main.route("/resendotp", methods=['GET', 'POST'])
def resend():
    if request.method == 'POST':
        if 'email' in session:
            emaildb = session['email'][0]
            x = generate_otp()  # generate otp
            send_otp(emaildb, x)  # resend otp
            d = session['email'][1]
            return render_template("verify.html", d=d)
    return redirect('/')


@main.route("/verify", methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        d = request.form['rollno']
        stuid = Student.query.get(d)
        if stuid is None:
            return render_template('email.html', msg="Please Enter Valid Roll NO")

        emaildb = stuid.email
        session['email'] = (emaildb, d)
        x = generate_otp()
        send_otp(emaildb, x)

        return render_template("verify.html", d=d)
    return render_template("email.html")


@main.route('/validate/<int:d>', methods=['GET', 'POST'])
def validate(d):
    if request.method == 'POST':
        f = Student.query.get(d)
        emaildb = f.email
        userotp = request.form['otp']
        if 'response' in session:
            s = session['response']
            session.pop('response', None)
            if s == str(userotp):

                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login('sturesultserver@gmail.com', 'nwcknlephjurfrgx')
                    subject = 'Result'
                    body = (str(f.name) + "\n Email: " + str(f.email) + "\n Math Marks: " + str(f.mtmarks) +
                            "\n Science Marks: " + str(f.scmarks)+ "\n Computer Marks: " + str(f.csmarks) +
                            "\n Total Marks:" + str(f.csmarks + f.mtmarks + f.scmarks) + "\n Percenatge: " +
                            str(round(((f.csmarks + f.mtmarks + f.scmarks)/300)*100)))

                    msg = f'Subject:{subject}\n\n{body}'
                    smtp.sendmail('sturesultserver@gmail.com', emaildb, msg)
                return render_template('result.html', f=f, d=d,
                                       msg="Result has been Send to your given respected Email Id")
        return render_template("email.html", msg="Wrong OTP!........Please Login Again")
        # return render_template('email.html')


@main.route('/download/<int:d>', methods=['GET', 'POST'])
def download(d):
    f = Student.query.get(d)
    rendered = render_template('result.html', f=f, msg="Result has been Send to your given respected Email Id")
    path_wkthmltopdf = b"C:\Program Files\wkhtmltopdf\\bin\wkhtmltopdf.exe"
    config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
    pdf = pdfkit.from_string(rendered, False, configuration=config)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=MyResult.pdf'
    return response
