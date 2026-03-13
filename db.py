import mysql.connector
from config import DB_CONFIG

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def init_db():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            name VARCHAR(255) NOT NULL,
            tag VARCHAR(100),
            target_days INT DEFAULT 30,
            interval_days INT DEFAULT 1,
            icon VARCHAR(100) DEFAULT 'star',
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habit_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            habit_id INT,
            log_date DATE,
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mini_goals (
            id INT AUTO_INCREMENT PRIMARY KEY,
            habit_id INT NOT NULL,
            title VARCHAR(255) NOT NULL,
            goal_date DATE NOT NULL,
            is_done BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
        )
    """)

    db.commit()
    cursor.close()
    db.close()