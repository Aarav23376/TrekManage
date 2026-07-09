from app import app,db
from app import models
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    admin=models.User.query.filter_by(role=models.ROLE_ADMIN).first()
    if admin is None:
        admin=models.User(
            full_name="Administrator",
            email="admin@trek.com",
            phone_number="9999999999",
            password_hash=generate_password_hash("admin123"),
            role=models.ROLE_ADMIN
        )
        db.session.add(admin)
        db.session.commit()


if __name__ == "__main__":
    app.run(debug=True)