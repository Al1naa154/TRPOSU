from flask import Blueprint, render_template, session, redirect, url_for, request
from functools import wraps
from db import get_db

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# ------------------ Проверка админа ------------------
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT role FROM users WHERE id=%s", (session["user_id"],))
        result = cursor.fetchone()
        cursor.close()
        db.close()
        if not result or result[0] != "admin":
            return "Доступ запрещён", 403
        return f(*args, **kwargs)
    return decorated

# ------------------ Панель администратора ------------------
@admin_bp.route("/")
@admin_required
def admin_panel():
    return render_template("admin_panel.html")


# ------------------ Список пользователей ------------------
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


# ------------------ Просмотр привычек конкретного пользователя ------------------
@admin_bp.route("/user/<int:user_id>")
@admin_required
def view_user(user_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Пользователь
    cursor.execute("SELECT id, email, role FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.close()
        db.close()
        return "Пользователь не найден", 404

    # Привычки
    cursor.execute("SELECT * FROM habits WHERE user_id=%s", (user_id,))
    habits = cursor.fetchall()

    # Мини-цели
    habit_ids = [h['id'] for h in habits]
    mini_goals = {}
    if habit_ids:
        format_strings = ','.join(['%s'] * len(habit_ids))
        cursor.execute(f"SELECT id, title, is_done, habit_id FROM mini_goals WHERE habit_id IN ({format_strings})", habit_ids)
        rows = cursor.fetchall()
        for row in rows:
            mini_goals.setdefault(row['habit_id'], []).append(row)

    cursor.close()
    db.close()
    return render_template("admin_user_view.html", user=user, habits=habits, mini_goals=mini_goals)


# ------------------ Логирование, добавление, редактирование и удаление привычек ------------------
@admin_bp.route("/user/<int:user_id>/log/<int:habit_id>")
@admin_required
def log_habit(user_id, habit_id):
    from services.habit_service import HabitService
    HabitService.log_today(habit_id)
    return redirect(url_for('admin.view_user', user_id=user_id))


@admin_bp.route("/user/<int:user_id>/add_habit", methods=["POST"])
@admin_required
def add_habit(user_id):
    from services.habit_service import Habit
    name = request.form["name"]
    tag = request.form.get("tag", "")
    target_days = int(request.form.get("target_days", 30))
    interval_days = int(request.form.get("interval_days", 1))
    icon = request.form.get("icon", "star")

    habit = Habit(user_id, name, tag, target_days, interval_days, icon)
    habit.save()
    return redirect(url_for('admin.view_user', user_id=user_id))


@admin_bp.route("/user/<int:user_id>/delete_habit/<int:habit_id>")
@admin_required
def delete_habit(user_id, habit_id):
    from services.habit_service import HabitService
    HabitService.delete(habit_id)
    return redirect(url_for('admin.view_user', user_id=user_id))


@admin_bp.route("/user/<int:user_id>/edit_habit/<int:habit_id>", methods=["GET", "POST"])
@admin_required
def edit_habit(user_id, habit_id):
    from db import get_db
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM habits WHERE id=%s", (habit_id,))
    habit = cursor.fetchone()
    cursor.close()
    db.close()
    if request.method == "POST":
        from services.habit_service import HabitService
        name = request.form["name"]
        tag = request.form.get("tag", "")
        target_days = int(request.form.get("target_days", 30))
        interval_days = int(request.form.get("interval_days", 1))
        icon = request.form.get("icon", habit[6])
        HabitService.update(habit_id, name, tag, target_days, interval_days, icon)
        return redirect(url_for('admin.view_user', user_id=user_id))
    return render_template("edit_habit.html", habit=habit)