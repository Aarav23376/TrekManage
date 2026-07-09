from app import models,db
from flask import render_template,request,session,flash
from flask import redirect,url_for
from werkzeug.security import check_password_hash,generate_password_hash
from datetime import datetime
from sqlalchemy import or_
from flask import Blueprint

auth = Blueprint("auth", __name__)


@auth.route("/")
def home():
    return render_template("home.html")

@auth.route("/login", methods=["POST"])
def login():
    # if request.method=="POST":
        print("Login route reached")
        email=request.form.get("email")
        password=request.form.get("password")
        user=models.User.query.filter_by(email=email).first()
        if user is None:
            return "User not found"
        else:    
            if check_password_hash(user.password_hash,password):

                if not user.approved:
                    flash("Awaiting admin approval.", "warning")
                    return redirect(url_for("auth.home", login="true"))
                
                if user.blacklisted:
                    flash("Your account has been blocked.", "danger")
                    return redirect(url_for("auth.home", login="true"))
                

                session["user_id"]=user.id
                if user.role==models.ROLE_ADMIN:
                    print("login complete")
                    return redirect(url_for("admin.admin_dashboard"))
                elif user.role==models.ROLE_STAFF:
                    return redirect(url_for("staff.staff_dashboard"))
                else:
                    return redirect(url_for("trekker.trekker_dashboard"))        
            else:
                flash("Invalid email or password", "danger")
                return redirect(url_for("auth.home", login="true"))
            
#                               /////////////////////////////////////////////////////////////////////////


@auth.route("/register", methods=["POST"])
def register():
    # if request.method=="POST":

        full_name=request.form.get("full_name")
        email=request.form.get("email")
        phone_number=request.form.get("phone_number")
        password=request.form.get("password")
        confirm_password=request.form.get("confirm_password")
        role=request.form.get("role")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.home"))
        
        existing_user = models.User.query.filter_by(email=email).first()

        if existing_user is not None:
            flash("Email already registered.", "warning")
            return redirect(url_for("auth.home"))
        
        existing_phone_number=models.User.query.filter_by(phone_number=phone_number).first()
        if existing_phone_number is not None:
            flash("Phone number already registered.", "warning")
            return redirect(url_for("auth.home"))
        
        if role not in [models.ROLE_TREKKER, models.ROLE_STAFF]:
            flash("Invalid Role.", "warning")
            return redirect(url_for("auth.home"))
        
        new_user=models.User(
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            password_hash=generate_password_hash(password),
            role=role,
            approved=role==models.ROLE_TREKKER,
            blacklisted=False
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful. Please login to continue.", "success")
        return redirect(url_for("auth.home", login="true"))
    # return redirect(url_for("home"))


@auth.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logged out successfully.", "success")
    return redirect(url_for("auth.home"))