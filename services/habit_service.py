from db import get_db
from datetime import date, timedelta


class HabitService:

    @staticmethod
    def get_all(user_id):
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT h.*, i.file_path
            FROM habits h
            LEFT JOIN icons i ON h.icon_id = i.id
            WHERE h.user_id = %s
        """, (user_id,))

        rows = cursor.fetchall()
        cursor.close()
        db.close()
        return rows

    @staticmethod
    def log_today(habit_id):
        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            "INSERT INTO habit_logs (habit_id, log_date) VALUES (%s, %s)",
            (habit_id, date.today())
        )

        db.commit()
        cursor.close()
        db.close()

    @staticmethod
    def delete(habit_id):
        db = get_db()
        cursor = db.cursor()

        cursor.execute("DELETE FROM habit_logs WHERE habit_id=%s", (habit_id,))
        cursor.execute("DELETE FROM habits WHERE id=%s", (habit_id,))

        db.commit()
        cursor.close()
        db.close()

    @staticmethod
    def calculate_streak(habit_id):
        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT log_date FROM habit_logs
            WHERE habit_id=%s
            ORDER BY log_date DESC
        """, (habit_id,))

        logs = [r[0] for r in cursor.fetchall()]
        cursor.close()
        db.close()

        streak = 0
        today = date.today()

        for log in logs:
            if log == today:
                streak += 1
                today -= timedelta(days=1)
            else:
                break

        return streak

    @staticmethod
    def get_log_set(habit_id):
        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            "SELECT log_date FROM habit_logs WHERE habit_id=%s",
            (habit_id,)
        )

        logs = {r[0] for r in cursor.fetchall()}
        cursor.close()
        db.close()

        return logs

    @staticmethod
    def get_day_statuses(habit):
        logs = HabitService.get_log_set(habit["id"])

        today = date.today()

        days = []

        for i in range(habit["target_days"]):
            d = today + timedelta(days=i * habit["interval_days"])

            if d in logs:
                status = "done"
            else:
                status = "missed"

            days.append({
                "date": d.strftime("%d.%m.%Y"),
                "status": status
            })

        return days