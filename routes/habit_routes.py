from flask import Blueprint, render_template, request, redirect, url_for, session
from db import get_db

from models.habit import Habit
from services.habit_service import HabitService
from services.icon_service import IconService
from services.mini_goal_service import MiniGoalService

habits = Blueprint("habits", __name__)


# =========================
# 📌 ГЛАВНАЯ + ФИЛЬТР ПО ТЕГАМ
# =========================
@habits.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]

    # 🔥 фильтр по тегу
    selected_tag = request.args.get("tag")

    habits_list = HabitService.get_all(user_id)
    icons = IconService.get_all()

    # фильтрация
    if selected_tag:
        habits_list = [
            h for h in habits_list
            if h["tag"] == selected_tag
        ]

    streaks = {
        h["id"]: HabitService.calculate_streak(h["id"])
        for h in habits_list
    }

    day_map = {
        h["id"]: HabitService.get_day_statuses(h)
        for h in habits_list
    }

    mini_goals = {
        h["id"]: MiniGoalService.get_for_today(h["id"])
        for h in habits_list
    }

    # список тегов
    all_tags = sorted(
        set(h["tag"] for h in HabitService.get_all(user_id) if h["tag"])
    )

    return render_template(
        "index.html",
        active_habits=habits_list,
        streaks=streaks,
        icons=icons,
        day_map=day_map,
        mini_goals=mini_goals,
        all_tags=all_tags,
        selected_tag=selected_tag
    )


# =========================
# ➕ ДОБАВИТЬ ПРИВЫЧКУ
# =========================
@habits.route("/add", methods=["POST"])
def add():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    habit = Habit(
        session["user_id"],
        request.form["name"],
        request.form.get("tag", ""),
        request.form.get("target_days", 30),
        request.form.get("interval_days", 1),
        request.form.get("icon_id")
    )

    habit.save()
    return redirect(url_for("habits.index"))


# =========================
# ✔ ОТМЕТИТЬ ДЕНЬ
# =========================
@habits.route("/log/<int:habit_id>")
def log(habit_id):
    HabitService.log_today(habit_id)
    return redirect(url_for("habits.index"))


# =========================
# 🗑 УДАЛИТЬ ПРИВЫЧКУ
# =========================
@habits.route("/delete/<int:habit_id>")
def delete(habit_id):
    HabitService.delete(habit_id)
    return redirect(url_for("habits.index"))


# =========================
# ✏ РЕДАКТИРОВАНИЕ ПРИВЫЧКИ
# =========================
@habits.route("/edit/<int:habit_id>", methods=["GET", "POST"])
def edit(habit_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # GET — открыть форму
    if request.method == "GET":
        cursor.execute("SELECT * FROM habits WHERE id=%s", (habit_id,))
        habit = cursor.fetchone()

        cursor.execute("SELECT id, file_path FROM icons")
        icons = cursor.fetchall()

        cursor.close()
        db.close()

        if not habit:
            return "Привычка не найдена", 404

        return render_template("edit_habit.html", habit=habit, icons=icons)

    # POST — сохранить
    name = request.form["name"]
    tag = request.form.get("tag", "")
    target_days = request.form.get("target_days", 30)
    interval_days = request.form.get("interval_days", 1)
    icon_id = request.form.get("icon_id")

    cursor.execute("""
        UPDATE habits
        SET name=%s,
            tag=%s,
            target_days=%s,
            interval_days=%s,
            icon_id=%s
        WHERE id=%s
    """, (name, tag, target_days, interval_days, icon_id, habit_id))

    db.commit()
    cursor.close()
    db.close()

    return redirect(url_for("habits.index"))


# =========================
# 🔥 MINI GOALS
# =========================
@habits.route("/mini_goal/add/<int:habit_id>", methods=["POST"])
def add_mini_goal(habit_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    title = request.form["title"]
    MiniGoalService.add(habit_id, title)

    return redirect(url_for("habits.index"))


@habits.route("/mini_goal/toggle/<int:goal_id>")
def toggle_mini_goal(goal_id):
    MiniGoalService.toggle(goal_id)
    return redirect(url_for("habits.index"))


@habits.route("/mini_goal/delete/<int:goal_id>")
def delete_mini_goal(goal_id):
    MiniGoalService.delete(goal_id)
    return redirect(url_for("habits.index"))