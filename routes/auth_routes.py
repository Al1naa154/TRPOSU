from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db

auth = Blueprint("auth", __name__)


# ------------------ Регистрация ------------------

@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        db = get_db()
        cursor = db.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (email, password) VALUES (%s, %s)",
                (email, password)
            )
            db.commit()
        except:
            db.rollback()
            cursor.close()
            db.close()
            return render_template(
                "register.html",
                error="Пользователь с таким email уже существует"
            )

        cursor.close()
        db.close()

        return redirect(url_for("auth.login"))

    return render_template("register.html")


# ------------------ Логин ------------------

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            "SELECT id, password, role FROM users WHERE email = %s",
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user and check_password_hash(user[1], password):
            session["user_id"] = user[0]
            session["role"] = user[2]

            return redirect(url_for("habits.index"))

        else:
            return render_template(
                "login.html",
                error="Неверный email или пароль"
            )

    return render_template("login.html")


# ------------------ Выход ------------------

@auth.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("role", None)
    return redirect(url_for("auth.login"))