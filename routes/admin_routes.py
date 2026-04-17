from flask import Blueprint, render_template, session, redirect, url_for
from functools import wraps
from db import get_db
from services.mini_goal_service import MiniGoalService

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ------------------ проверка админа ------------------
def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT role FROM users WHERE id=%s", (session["user_id"],))
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if not user or user[0] != "admin":
            return "Доступ запрещён", 403

        return f(*args, **kwargs)

    return wrapper


# ------------------ список пользователей ------------------
@admin_bp.route("/users")
@admin_required
def users_list():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, email, role FROM users")
    users = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template("admin_users.html", users=users)


# ------------------ просмотр пользователя + отметки ------------------
@admin_bp.route("/user/<int:user_id>")
@admin_required
def view_user(user_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # user
    cursor.execute("SELECT id, email, role FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.close()
        db.close()
        return "Пользователь не найден", 404

    # habits
    cursor.execute("SELECT * FROM habits WHERE user_id=%s", (user_id,))
    habits = cursor.fetchall()

    # logs (ВСЕ отметки пользователя)
    cursor.execute("""
        SELECT habit_id, log_date 
        FROM habit_logs
        WHERE habit_id IN (
            SELECT id FROM habits WHERE user_id=%s
        )
        ORDER BY log_date
    """, (user_id,))
    logs = cursor.fetchall()

    cursor.close()
    db.close()

    # группируем отметки по привычкам
    logs_map = {}
    for log in logs:
        logs_map.setdefault(log["habit_id"], []).append(log["log_date"])

    # мини-цели
    mini_goals = {}
    for h in habits:
        mini_goals[h["id"]] = MiniGoalService.get_for_today(h["id"])

    return render_template(
        "admin_user_view.html",
        user=user,
        habits=habits,
        logs_map=logs_map,
        mini_goals=mini_goals
    )