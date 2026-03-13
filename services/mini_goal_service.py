from db import get_db
from datetime import date

class MiniGoalService:

    @staticmethod
    def get_for_today(habit_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT id, title, is_done 
            FROM mini_goals 
            WHERE habit_id = %s AND goal_date = %s
        """, (habit_id, date.today()))
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        return rows

    @staticmethod
    def add(habit_id, title):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO mini_goals (habit_id, title, goal_date)
            VALUES (%s, %s, %s)
        """, (habit_id, title, date.today()))
        db.commit()
        cursor.close()
        db.close()

    @staticmethod
    def toggle(goal_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            UPDATE mini_goals 
            SET is_done = NOT is_done 
            WHERE id = %s
        """, (goal_id,))
        db.commit()
        cursor.close()
        db.close()

    @staticmethod
    def delete(goal_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM mini_goals WHERE id = %s", (goal_id,))
        db.commit()
        cursor.close()
        db.close()