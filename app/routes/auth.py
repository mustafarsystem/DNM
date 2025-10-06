from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from werkzeug.security import check_password_hash
from app.extensions import db
from app.models import Users
from forms import LoginForm

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = db.session.execute(db.select(Users).where(Users.email == email)).scalar()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("index"))  # Ana sayfana yönlendir
        else:
            flash("Email ya da şifre hatalı")
            return redirect(url_for("auth.login"))
    return render_template("login.html", form=form, logged_in=current_user.is_authenticated, user=current_user)

@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))