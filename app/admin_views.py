from flask import Blueprint, session, request, render_template, redirect, flash
from .models import Student, db
import os
from flask_admin import Admin   #admin
from flask_admin.contrib.sqla import ModelView    #admin
from werkzeug.exceptions import abort    #admin

main2 = Blueprint('main2', __name__)
admin = Admin()


@main2.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username.strip() == "admin" and password.strip() == "12345":
            session['username'] = username
            return redirect("/admin")
        else:
            msg = " Invalid username/ password"
            return render_template("login.html", msg=msg)
    return render_template("login.html")


@main2.route("/logout")
def logout():
    session.pop('username')
    return render_template('login.html')


@main2.route("/admin", methods=['GET', 'POST'])
def admin2():
    if "username" in session:
        page = request.args.get('page', 1, type=int)
        all_data = Student.query.order_by(Student.stuid.asc()).paginate(page=int(page), per_page=5)
        return render_template('index1.html', alldata=all_data)
    else:
        return redirect('/')


@main2.route('/add', methods=['GET', 'POST'])
def add_stu():
    if "username" in session:
        if request.method == 'POST':
            stuid = request.form.get('stuid')
            stu_name = request.form.get('name')
            email = request.form.get('email')
            mobile_no = request.form.get('mbno')
            math_marks = request.form.get('mtmarks')
            science_marks = request.form.get('scmarks')
            computer_marks = request.form.get('csmarks')

            all_data = Student.query.all()
            for student in all_data:
                if student.email == email:
                    flash(f"This data already exits: {email} ", "info")
                    return redirect('/admin')
                elif student.stuid == int(stuid):
                    flash(f"This data already exits: {stuid} ", "info")
                    return redirect('/admin')

            stu = Student(stuid=stuid.strip(), name=stu_name.strip(), email=email.strip(),
                          mbno=mobile_no.strip(), mtmarks=math_marks.strip(), scmarks=science_marks.strip(),
                          csmarks=computer_marks.strip())
            db.session.add(stu)
            db.session.commit()
            flash(f"Data inserted successfully ", "info")
            return redirect('/admin')
        return render_template('add.html')
    return redirect('/')


@main2.route("/update/<int:stuid>", methods=['GET', 'POST'])
def update(stuid):
    if "username" in session:
        if request.method == 'POST':
            stuid = request.form.get('stuid')
            stu_name = request.form.get('name')
            email = request.form.get('email')
            mobile_no = request.form.get('mbno')
            math_marks = request.form.get('mtmarks')
            science_marks = request.form.get('scmarks')
            computer_marks = request.form.get('csmarks')
            stu = Student.query.filter_by(stuid=stuid).first()
            stu.stuid = stuid
            stu.name = stu_name
            stu.email = email
            stu.mbno = mobile_no
            stu.mtmarks = math_marks
            stu.scmarks = science_marks
            stu.csmarks = computer_marks
            try:
                db.session.add(stu)
                db.session.commit()
            except Exception:
                db.session.rollback()
                flash(f"This email already exits", "info")
                return redirect('/admin')
            flash(f"Data updated successfully ", "info")
            return redirect("/admin")

        stu = Student.query.filter_by(stuid=stuid).first()
        return render_template('update.html', stu=stu)
    else:
        return redirect("/")


@main2.route("/delete/<int:stuid>")
def delete(stuid):
    if "username" in session:
        stu = Student.query.filter_by(stuid=stuid).first()
        db.session.delete(stu)
        db.session.commit()
        flash(f"Data deleted successfully ", "danger")
        return redirect("/admin")
    else:
        return redirect("/")


@main2.route('/search', methods=['GET', 'POST'])
def search():
    if 'username' in session:
        if request.method == 'POST' and 'tag' in request.form:
            tag = request.form.get('tag')
            search = "%{}%".format(tag)
            page = request.args.get('page', 1, type=int)
            all_data = Student.query.filter(Student.name.like(search)).paginate(per_page=20, page=int(page))
            return render_template('index1.html', alldata=all_data, tag=tag)
        return render_template("email.html")
    return redirect('/')

