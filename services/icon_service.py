from db import get_db

class IconService:
    @staticmethod
    def get_all():
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, name, file_path 
            FROM icons
            WHERE file_path IS NOT NULL AND file_path != ''
        """)

        icons = cursor.fetchall()

        cursor.close()
        db.close()

        return icons