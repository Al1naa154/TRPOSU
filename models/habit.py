from db import get_db
class Habit:
    def __init__(self, user_id, name, tag, target_days=30, interval_days=1, icon_id=None):
        self.user_id = user_id
        self.name = name
        self.tag = tag
        self.target_days = target_days
        self.interval_days = interval_days
        self.icon_id = icon_id

    def save(self):
        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO habits
            (user_id, name, tag, target_days, interval_days, icon_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            self.user_id,
            self.name,
            self.tag,
            self.target_days,
            self.interval_days,
            self.icon_id
        ))

        db.commit()
        cursor.close()
        db.close()