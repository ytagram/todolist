from __future__ import with_statement
from distutils.log import error
from multiprocessing.dummy import Value
from tokenize import Name
from unicodedata import name
from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from time import time


app = Flask(__name__)
app.secret_key = "hello"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=5)

db = SQLAlchemy(app)


app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = "robottesting666@gmail.com"
app.config['MAIL_DEFAULT_SENDER'] = ('admin','robottesting666@gmail.com')
app.config["MAIL_PASSWORD"] = "Testing666"

mail = Mail(app)

class users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))
    todos = db.relationship(
        'todos',
        backref='users', 
        lazy='dynamic'
    )

    def __init__(self,id,name,email,password):
        self.id = id
        self.name = name
        self.email = email
        self.password = password


class todos(db.Model):
    __tablename__ = 'todos'
    _tid = db.Column(db.Integer, primary_key=True)
    tname = db.Column(db.String(100))
    content = db.Column(db.String(100))
    date = db.Column(db.Date(),nullable=True)
    time = db.Column(db.Time(),nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self,tname,content,date,time,user_id):
        self.tname = tname
        self.content = content
        self.user_id = user_id
        self.date = date
        self.time = time


@app.route("/")
def home():
    if "id" in session:
        id = session["id"]
        found_user = users.query.filter_by(id=id).first()
        if found_user:
            return render_template("user.html",name=found_user.name)
        else: 
            return render_template("login.html")
    else:
        return render_template("login.html",)

@app.route("/view")
def view():
    if "id" in session:
        id = session["id"]
        return render_template("view.html", values=users.query.all())
    else:
        flash("You are not logged in!")
        return redirect(url_for("login"))

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        session.permanent = True
        id = request.form["id"]
        name = request.form["nm"]
        email = request.form["email"]
        password = request.form["pw"]
        confirmpw = request.form["confirmpw"]
        found_user = users.query.filter_by(id=id).first()
        if found_user: 
            flash('User ID already exist, please try again')
            return render_template("register.html")
        else:
            if confirmpw == password:
                usr = users(id,name,email,password=generate_password_hash(password, method='sha256'))
                db.session.add(usr)
                db.session.commit()
                session["id"] = id
                return redirect(url_for("user"))
            else:
                flash('Password does not match!')
                return render_template("register.html")
    else:
        if "id" in session:
            flash("Already Logged in!")
            return redirect(url_for("user"))
    return render_template("register.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        id = request.form["id"]
        password = request.form["pw"]
        found_user = users.query.filter_by(id=id).first()
        if found_user:
            if check_password_hash(found_user.password, password):
                session["id"] = id
                return redirect(url_for("user"))
            else:
                flash("Incorrent password!")
                return render_template("login.html")
        else:
            flash("User ID does not exist.")
            return render_template("login.html")
    else:
        if "id" in session:
            return redirect(url_for("user"))
    return render_template("login.html")

@app.route("/user", methods=["POST", "GET"])
def user():
    if "id" in session:
        id = session["id"]
        found_user = users.query.filter_by(id=id).first()
        if found_user:
            return  render_template("user.html", name=found_user.name)
        return render_template("user.html")
    else:
        return redirect(url_for("login"))

@app.route("/myprofile", methods=["POST", "GET"])
def myprofile():
    if "id" in session:
        id = session["id"]
        found_user = users.query.filter_by(id=id).first()
        if found_user:
            return render_template('myprofile.html',usr=id,name=found_user.name,email=found_user.email)        
        else:
            return redirect(url_for("user"))                           
    else:
        return redirect(url_for("login"))

@app.route("/deleteacc", methods=["POST", "GET"])
def deleteacc():
    if "id" in session:
        id = session["id"]
        found_user = users.query.filter_by(id=id).first()
        if found_user:
            if request.method == "POST" and request.values['send']=='delete my profile':
                password = request.form["pw"]
                if check_password_hash(found_user.password, password):
                    db.session.query(todos).filter_by(user_id=id).delete()
                    db.session.delete(found_user)
                    db.session.commit()
                    session.pop("id", None)
                    return redirect(url_for("login"))
                flash("Password INcorrect!")
                return redirect(url_for("deleteacc"))
            return render_template('deleteacc.html',usr=id,name=found_user.name)        
        else:
            return redirect(url_for("user"))                           
    else:
        flash("You are not logged in!")
        return redirect(url_for("login"))

@app.route("/profile", methods=["POST", "GET"])
def profile():
    email = None
    if "id" in session:
        id = session["id"]
        found_user = users.query.filter_by(id=id).first()
        if found_user:
            if request.method == "POST":
                if request.values['send']=='change': 
                    newname = request.form["nm"]
                    newemail = request.form["email"]
                    password = request.form["pw"]
                    if  check_password_hash(found_user.password, password):
                        found_user.name = newname
                        found_user.email = newemail
                        db.session.commit()
                        return redirect(url_for("myprofile"))
                    else:
                        flash("Password INcorrect!")
                        return redirect(url_for("profile"))
        return render_template('profile.html',usr=id,name=found_user.name,email=found_user.email)
    else:
        flash("You are not logged in!")
        return redirect(url_for("login"))

@app.route("/changepw", methods=["POST", "GET"])
def changepw():
    email = None
    if "id" in session:
        id = session["id"]
        found_user = users.query.filter_by(id=id).first()
        if found_user:
            if request.method == "POST":
                if request.values['send']=='change': 
                    newpassword = request.form["newpw"]
                    newpasswordconfim = request.form["confirmnewpw"]
                    password = request.form["pw"]
                    if newpassword == newpasswordconfim:
                        if check_password_hash(found_user.password, password):
                            found_user.password = generate_password_hash(newpassword,method='sha256')
                            db.session.commit()
                            return redirect(url_for("myprofile"))
                        else:
                            flash("New password doen not match!")
                        return redirect(url_for("changepw"))
                    else:
                        flash("Old password INcorrect!")
                        return redirect(url_for("changepw"))
        return render_template('changepw.html',usr=id,name=found_user.name)

    else:
        flash("You are not logged in!")
        return redirect(url_for("login"))

@app.route("/todo", methods=["POST", "GET"])
def todo():
    if "id" in session:
        id = session["id"]
        found_user = users.query.filter_by(id=id).first()
        found_todo = todos.query.filter_by(user_id=id).all()
        if found_todo:
            return render_template("todo.html", name=found_user.name, todos=found_todo,)
        else:
            return render_template("todo.html", name=found_user.name, todos=found_todo)
    else:
        flash("You are not logged in!")
        return redirect(url_for("login"))

@app.route("/addtodo", methods=["POST", "GET"])
def addtodo():
    if "id" in session:
        id = session["id"]
        found_user = users.query.filter_by(id=id).first()
        if request.method == "POST":
            if request.values['send']=='add':
                tname = request.form["tnm"]
                content = request.form["cont"]
                time = None
                date = None
                if request.form["date"]:
                    date = datetime.strptime(request.form["date"], "%Y-%m-%d").date()
                if request.form["time"]:
                    timestr = str(request.form["time"])
                    time = datetime.strptime(timestr, "%H:%M").time()
                todo = todos(tname,content,date,time,id)
                db.session.add(todo)
                db.session.commit()
                return redirect(url_for("todo"))
        return render_template("addtodo.html", name=found_user.name)
    else:
        flash("You are not logged in!")
        return redirect(url_for("login"))


@app.route("/updatetodo/<tid>", methods=["POST", "GET"])
def updatetodo(tid):
    if "id" in session:
        id = session["id"]
        found_user = users.query.filter_by(id=id).first()
        found_todo = todos.query.filter_by(_tid=tid).first()
        if found_todo and found_user.id == found_todo.user_id:
            if request.method == "POST":
                if request.values['send']=='update':
                        found_todo.tname = request.form["tnm"]
                        found_todo.content = request.form["cont"]
                        found_todo.date = None
                        found_todo.time = None
                        if(request.form["date"]):
                            found_todo.date = datetime.strptime(request.form["date"], "%Y-%m-%d").date()
                        if(request.form["time"]):
                            time = str(request.form["time"])
                            found_todo.time = datetime.strptime(time, "%H:%M").time()
                        db.session.commit()
                        return redirect(url_for("todo"))
                if request.values['send']=='delete':
                    db.session.delete(found_todo)
                    db.session.commit()
                    return redirect(url_for("todo"))
            timestr = str(found_todo.time)
            timestr = timestr[0:-3]
            return render_template('updatetodo.html',name=found_user.name,tname=found_todo.tname,content=found_todo.content,date=found_todo.date,time=timestr)    
        else:
            return redirect(url_for("todo"))
    else:
        flash("You are not logged in!")
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    if "id" in session:
        id = session["id"]
        session.pop("id", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    db.create_all()
    # found = todos.query.filter_by(_tid=1).first()
    # found2 = todos.query.filter_by(_tid=2).first()
    # db.session.delete(found)
    # db.session.delete(found2)
    # admin = users('0000','admin', 'root@email.com','1234')
    # t1 = todos('study', '123456','', '123')
    # t2 = todos('work', 'do work', '123')
    # db.session.add_all([admin])
    # db.session.add_all([u1, t1, t2])
    # db.session.commit()
    app.run()