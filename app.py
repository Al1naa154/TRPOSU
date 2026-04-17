from flask import Flask
from config import SECRET_KEY
from db import init_db

from routes.auth_routes import auth        # auth = Blueprint("auth", ...)
from routes.habit_routes import habits     # habits = Blueprint("habits", ...)
from routes.admin_routes import admin_bp   # ⚠ Импортируем admin_bp, а не admin

app = Flask(__name__)
app.secret_key = SECRET_KEY

print("APP LOADED")

# Регистрируем blueprint'ы
app.register_blueprint(auth)
app.register_blueprint(habits)
app.register_blueprint(admin_bp)  # ⚠ Используем admin_bp

if __name__ == "__main__":
    init_db()
    app.run(debug=True)