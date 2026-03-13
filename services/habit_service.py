from db import get_db
from datetime import date, timedelta

class HabitService:
    @staticmethod
    def get_all(user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM habits WHERE user_id = %s", (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        return rows
    
    @staticmethod
    def get_tags(user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT DISTINCT tag FROM habits 
            WHERE user_id = %s AND tag IS NOT NULL AND tag != ''
        """, (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        return [r[0] for r in rows]

    @staticmethod
    def log_today(habit_id):
        today = date.today()
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO habit_logs (habit_id, log_date) VALUES (%s, %s)",
            (habit_id, today)
        )
        db.commit()
        cursor.close()
        db.close()

    @staticmethod
    def get_logs(habit_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT log_date FROM habit_logs WHERE habit_id = %s ORDER BY log_date",
            (habit_id,)
        )
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        return [r[0] for r in rows]

    @staticmethod
    def calculate_streak(habit_id):
        logs = HabitService.get_logs(habit_id)
        streak = 0
        current_day = date.today()
        for log in reversed(logs):
            if log == current_day:
                streak += 1
                current_day -= timedelta(days=1)
            else:
                break
        return streak

    @staticmethod
    def is_completed(habit):
        habit_id = habit[0]
        target_days = habit[4]
        streak = HabitService.calculate_streak(habit_id)
        return streak >= target_days

    @staticmethod
    def delete(habit_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM habit_logs WHERE habit_id = %s", (habit_id,))
        cursor.execute("DELETE FROM habits WHERE id = %s", (habit_id,))
        db.commit()
        cursor.close()
        db.close()

    @staticmethod
    def get_log_set(habit_id):
        """Множество дат, когда привычка была выполнена"""
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT log_date FROM habit_logs WHERE habit_id = %s",
            (habit_id,)
        )
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        return set(r[0] for r in rows)


    @staticmethod
    def get_day_statuses(habit):
        """
        Возвращает список словарей:
        [{date, status}] где status = future | done | missed
        """
        habit_id = habit[0]
        target_days = habit[4]
        interval = habit[5] if len(habit) > 5 else 1  # Новое поле interval_days

        logs = HabitService.get_log_set(habit_id)
        if not logs:
            start_date = date.today()
        else:
           start_date = min(logs)

        days = []
        today = date.today()

        for i in range(target_days):
            d = start_date + timedelta(days=i*interval)

            if d > today:
                status = "future"
            elif d in logs:
                status = "done"
            else:
                status = "missed"

            days.append({
                "date": d.strftime("%d.%m.%Y"),
                "status": status
            })

        return days