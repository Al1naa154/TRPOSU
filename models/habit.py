from db import get_db

class Habit:
    def __init__(self, user_id, name, tag, target_days=30, interval_days=1, icon="star"):
        self.user_id = user_id
        self.name = name
        self.tag = tag
        self.target_days = target_days
        self.interval_days = interval_days
        self.icon = icon

    def save(self):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO habits (user_id, name, tag, target_days, interval_days, icon) VALUES (%s, %s, %s, %s, %s, %s)",
            (self.user_id, self.name, self.tag, self.target_days, self.interval_days, self.icon)
        )
        db.commit()
        cursor.close()
        db.close()