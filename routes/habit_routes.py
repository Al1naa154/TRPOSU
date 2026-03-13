from flask import Blueprint, render_template, request, redirect, url_for, session
from db import get_db
from models.habit import Habit
from services.habit_service import HabitService
from services.mini_goal_service import MiniGoalService


habits = Blueprint("habits", __name__)

ICON_LIST = [
    "star", "favorite", "alarm", "pets", "work", "fitness_center",
    "book", "lightbulb", "cake", "brush", "music_note", "sports_soccer",
    "directions_run", "eco", "face", "emoji_events", "flight", "local_cafe",
    "school", "shopping_cart", "spa", "check_circle", "bolt", "beach_access",
    "home", "code", "restaurant", "camera_alt", "movie", "palette",
    "directions_bike", "directions_car", "local_hospital",
    "nature_people", "emoji_food_beverage"
]


# ------------------ Главная ------------------

@habits.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]
    tag_filter = request.args.get("tag_filter", "")

    habits_list = HabitService.get_all(user_id)
    tags = HabitService.get_tags(user_id)

    if tag_filter:
        habits_list = [h for h in habits_list if h[3] == tag_filter]

    streaks = {h[0]: HabitService.calculate_streak(h[0]) for h in habits_list}

    active = [h for h in habits_list if not HabitService.is_completed(h)]
    completed = [h for h in habits_list if HabitService.is_completed(h)]

    mini_goals = {
        h[0]: MiniGoalService.get_for_today(h[0])
        for h in habits_list
    }

    day_map = {
        h[0]: HabitService.get_day_statuses(h)
        for h in habits_list
    }

    return render_template(
        "index.html",
        active_habits=active,
        completed_habits=completed,
        streaks=streaks,
        tags=tags,
        current_filter=tag_filter,
        mini_goals=mini_goals,
        day_map=day_map,
        icons=ICON_LIST,
        habit_icon="star"
    )


# ------------------ Добавление привычки ------------------

@habits.route("/add", methods=["POST"])
def add():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]

    name = request.form["name"]
    tag = request.form.get("tag", "")
    target_days = int(request.form.get("target_days", 30))
    interval_days = int(request.form.get("interval_days", 1))
    icon = request.form.get("icon", "star")

    habit = Habit(user_id, name, tag, target_days, interval_days, icon)
    habit.save()

    return redirect(url_for("habits.index"))


# ------------------ Отметить выполнение ------------------

@habits.route("/log/<int:habit_id>")
def log(habit_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    HabitService.log_today(habit_id)
    return redirect(url_for("habits.index"))


# ------------------ Удаление ------------------

@habits.route("/delete/<int:habit_id>")
def delete(habit_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    HabitService.delete(habit_id)
    return redirect(url_for("habits.index"))


# ------------------ Редактирование ------------------

@habits.route("/edit/<int:habit_id>", methods=["GET", "POST"])
def edit(habit_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM habits WHERE id = %s", (habit_id,))
    habit = cursor.fetchone()
    cursor.close()
    db.close()

    if not habit:
        return redirect(url_for("habits.index"))

    if request.method == "POST":
        name = request.form["name"]
        tag = request.form.get("tag", "")
        target_days = int(request.form.get("target_days", 30))
        interval_days = int(request.form.get("interval_days", 1))
        icon = request.form.get("icon", habit[6])

        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            UPDATE habits 
            SET name = %s, tag = %s, target_days = %s, 
                interval_days = %s, icon = %s 
            WHERE id = %s
            """,
            (name, tag, target_days, interval_days, icon, habit_id)
        )
        db.commit()
        cursor.close()
        db.close()

        return redirect(url_for("habits.index"))

    return render_template(
        "edit.html",
        habit=habit,
        icons=ICON_LIST,
        habit_icon=habit[6]
    )


# ------------------ Мини-цели ------------------

@habits.route("/mini_goal/add/<int:habit_id>", methods=["POST"])
def add_mini_goal(habit_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    title = request.form["title"]
    MiniGoalService.add(habit_id, title)

    return redirect(url_for("habits.index"))


@habits.route("/mini_goal/toggle/<int:goal_id>")
def toggle_mini_goal(goal_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    MiniGoalService.toggle(goal_id)
    return redirect(url_for("habits.index"))


@habits.route("/mini_goal/delete/<int:goal_id>")
def delete_mini_goal(goal_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    MiniGoalService.delete(goal_id)
    return redirect(url_for("habits.index"))