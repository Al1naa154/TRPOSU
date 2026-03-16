import mysql.connector
from config import DB_CONFIG

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def init_db():
    db = get_db()
    cursor = db.cursor()

    # ------------------ Таблица пользователей ------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'user'
        )
    """)

    # ------------------ Таблица привычек ------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            name VARCHAR(255) NOT NULL,
            tag VARCHAR(100),
            target_days INT DEFAULT 30,
            interval_days INT DEFAULT 1,
            icon VARCHAR(100) DEFAULT 'star',
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # ------------------ Таблица логов привычек ------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habit_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            habit_id INT NOT NULL,
            log_date DATE NOT NULL,
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
        )
    """)

    # ------------------ Таблица мини-целей ------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mini_goals (
            id INT AUTO_INCREMENT PRIMARY KEY,
            habit_id INT NOT NULL,
            title VARCHAR(255) NOT NULL,
            goal_date DATE NOT NULL,
            is_done TINYINT(1) DEFAULT 0,
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
        )
    """)

    db.commit()
    cursor.close()
    db.close()