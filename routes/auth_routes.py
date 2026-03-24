from flask import Blueprint, render_template, request, redirect, url_for, session
from db import get_db
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint("auth", __name__)

@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO users (email, password, role) VALUES (%s, %s, %s)",
            (email, password, "user")
        )
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for("auth.login"))
    return render_template("register.html")

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, password FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if user and check_password_hash(user[1], password):
            session["user_id"] = user[0]

            # Проверка роли
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT role FROM users WHERE id=%s", (user[0],))
            role = cursor.fetchone()[0]
            cursor.close()
            db.close()

            if role == "admin":
                return redirect(url_for("admin.admin_panel"))
            else:
                return redirect(url_for("habits.index"))

        return "Неверный email или пароль"
    return render_template("login.html")

@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))