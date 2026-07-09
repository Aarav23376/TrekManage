from flask import Flask,session
from config import Config
from flask_sqlalchemy import SQLAlchemy




db = SQLAlchemy()
app=Flask(__name__)


app.config.from_object(Config)
db.init_app(app)


from app import models


from app.routes.auth import auth
from app.routes.admin import admin
from app.routes.trekker import trekker
from app.routes.staff import staff

app.register_blueprint(auth)
app.register_blueprint(admin)
app.register_blueprint(trekker)
app.register_blueprint(staff)

@app.context_processor
def inject_current_user():
    if "user_id" in session:
        return {
            "current_user": models.User.query.get(session["user_id"])
        }
    return {
        "current_user": None
    }