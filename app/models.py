from app import db
from datetime import datetime,UTC

ROLE_ADMIN = "ADMIN"
ROLE_STAFF = "STAFF"
ROLE_TREKKER = "TREKKER"


class User(db.Model):
    __tablename__ = "users"

    id=db.Column(db.Integer,primary_key=True)
    full_name=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(120),unique=True,nullable=False)
    phone_number = db.Column(db.String(15),unique=True,nullable=False)
    password_hash=db.Column(db.String(255),nullable=False)
    role=db.Column(db.String(20),nullable=False)
    approved = db.Column(db.Boolean,default=True)
    blacklisted=db.Column(db.Boolean,default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    assigned_treks=db.relationship("Trek",back_populates="assigned_staff",lazy=True)
    bookings=db.relationship("Booking",backref="user",lazy=True)

class Trek(db.Model):
    __tablename__="treks"

    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    location= db.Column(db.String(100),nullable=False)
    difficulty=db.Column(db.String(20),nullable=False)  
    duration=db.Column(db.Integer,nullable=False) 
    start_date=db.Column(db.Date,nullable=False)
    end_date=db.Column(db.Date,nullable=False)
    available_slots=db.Column(db.Integer,nullable=False)
    description=db.Column(db.Text)
    status=db.Column(db.String(20),nullable=False)

    assigned_staff_id=db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)
    assigned_staff = db.relationship( "User",back_populates="assigned_treks",lazy=True)
    bookings=db.relationship("Booking",backref="trek",lazy=True)



class Booking(db.Model):
    __tablename__="bookings"

    id=db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)
    trek_id=db.Column(db.Integer,db.ForeignKey("treks.id"),nullable=False)
    booking_date=db.Column(db.Date,default=lambda: datetime.now(UTC).date())
    status=db.Column(db.String(20),nullable=False)

