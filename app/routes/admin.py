from app import models,db
from flask import render_template,request,session,flash
from flask import redirect,url_for
from werkzeug.security import check_password_hash,generate_password_hash
from datetime import datetime
from sqlalchemy import or_
from flask import Blueprint

admin = Blueprint("admin", __name__)


@admin.route("/admin/dashboard")
def admin_dashboard():
    
    if "user_id" not in session:
        return redirect(url_for("auth.home"))
        
    total_treks=models.Trek.query.count()
    total_staff=models.User.query.filter_by(role=models.ROLE_STAFF,approved=True,blacklisted=False).count()
    total_trekkers=models.User.query.filter_by(role=models.ROLE_TREKKER,blacklisted=False).count()
    total_bookings = models.Booking.query.count()

    recent_bookings=models.Booking.query.order_by(models.Booking.booking_date.desc()).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        total_treks=total_treks,
        total_staff=total_staff,
        total_trekkers=total_trekkers,
        total_bookings=total_bookings,
        recent_bookings=recent_bookings
    )    

#                   ///////////////////////////////////////////////////////////////////////////////

@admin.route("/admin/staff")
def manage_staff():

    if "user_id" not in session:
        return redirect(url_for("auth.home"))
    

    pending_staff=models.User.query.filter_by(role=models.ROLE_STAFF,approved=False).all()
    approved_staff=models.User.query.filter_by(role=models.ROLE_STAFF,approved=True,blacklisted=False).all()
    blacklisted_staff=models.User.query.filter_by(role=models.ROLE_STAFF,blacklisted=True).all()

    tab = request.args.get("tab", "pending")

    if tab=="approved":
        staff_list=approved_staff
    elif tab=="blacklisted":
        staff_list=blacklisted_staff
    else:
        staff_list=pending_staff

    counts={
        "pending":len(pending_staff),
        "approved":len(approved_staff),
        "blacklisted":len(blacklisted_staff)
    }
    return render_template("admin/staff.html",staff_list=staff_list,tab=tab,counts=counts)





@admin.route("/admin/staff/<int:staff_id>/approve", methods=["POST"])
def approve_staff(staff_id):

    if "user_id" not in session:
        return redirect(url_for("auth.home"))
    

    staff = models.User.query.get_or_404(staff_id)

    staff.approved = True
    db.session.commit()

    flash("Staff approved successfully.", "success")
    return redirect(url_for("admin.manage_staff", tab="pending"))



@admin.route("/admin/staff/<int:staff_id>/reject", methods=["POST"])
def reject_staff(staff_id):

    if "user_id" not in session:
        return redirect(url_for("auth.home"))
    

    staff = models.User.query.get_or_404(staff_id)

    db.session.delete(staff)
    db.session.commit()

    flash("Staff request rejected.", "danger")
    return redirect(url_for("admin.manage_staff", tab="pending"))


@admin.route("/admin/staff/<int:staff_id>/blacklist", methods=["POST"])
def blacklist_staff(staff_id):

    if "user_id" not in session:
        return redirect(url_for("auth.home"))
    
    staff = models.User.query.get_or_404(staff_id)

    staff.blacklisted = True
    db.session.commit()

    flash("Staff blacklisted successfully.", "success")
    return redirect(url_for("admin.manage_staff", tab="approved"))



@admin.route("/admin/staff/<int:staff_id>/unblacklist", methods=["POST"])
def unblacklist_staff(staff_id):
    if "user_id" not in session:
        return redirect(url_for("auth.home"))
    

    staff = models.User.query.get_or_404(staff_id)

    staff.blacklisted = False
    db.session.commit()

    flash("Staff reinstated successfully.", "success")
    return redirect(url_for("admin.manage_staff", tab="blacklisted"))

#                 ///////////////////////////////////////////////////////////////////////////////////////////



@admin.route("/admin/treks")
def manage_treks():

    if "user_id" not in session:
        return redirect(url_for("auth.home"))

    q = request.args.get("q", "").strip()

    treks = models.Trek.query

    if q:
        treks = treks.filter(
            db.or_(
                models.Trek.name.ilike(f"%{q}%"),
                models.Trek.location.ilike(f"%{q}%"),
                models.Trek.difficulty.ilike(f"%{q}%"),
                models.Trek.status.ilike(f"%{q}%")
            )
        )

    treks = treks.order_by(models.Trek.start_date.desc()).all()

    return render_template(
        "admin/treks.html",
        treks=treks,
        q=q
    )


@admin.route("/admin/treks/add", methods=["GET", "POST"])
def add_trek():

    if "user_id" not in session:
        return redirect(url_for("auth.home"))
    
    staff_options = models.User.query.filter_by(role=models.ROLE_STAFF,approved=True,blacklisted=False).all()
    if request.method=="POST":

        
        name = request.form.get("name")
        location = request.form.get("location")
        difficulty = request.form.get("difficulty")
        # duration = request.form.get("duration")
        available_slots = request.form.get("available_slots")
        description = request.form.get("description")
        status = request.form.get("status")
        assigned_staff_id = request.form.get("assigned_staff_id")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        duration = int(duration)
        available_slots = int(available_slots)
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        start_date = datetime.strptime(request.form["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(request.form["end_date"], "%Y-%m-%d").date()

        if end_date < start_date:
            flash("End date cannot be earlier than start date.", "danger")
            return redirect(request.url)
        
        today = datetime.today().date()

        if start_date < today:
            flash("Start date cannot be before today.", "danger")
            return redirect(request.url)
        
        duration = (end_date - start_date).days + 1

        trek=models.Trek(
            name=name,
            location=location,
            difficulty=difficulty,
            duration=duration,
            available_slots=available_slots,
            description=description,
            status=status,
            assigned_staff_id=assigned_staff_id if assigned_staff_id else None,
            start_date=start_date,
            end_date=end_date        
        )

        db.session.add(trek)
        db.session.commit()

        flash("Trek added successfully!", "success")
        return redirect(url_for("admin.manage_treks"))
    

    return  render_template("admin/trek_form.html",trek=None,form=None,staff_options=staff_options)


@admin.route("/admin/treks/edit/<int:trek_id>", methods=["GET", "POST"])
def edit_trek(trek_id):

    if "user_id" not in session:
        return redirect(url_for("auth.home"))
    

    trek = models.Trek.query.get_or_404(trek_id)

    staff_options = models.User.query.filter_by(
        role=models.ROLE_STAFF,
        approved=True,
        blacklisted=False
    ).all()

    if request.method == "POST":
        name = request.form.get("name")
        location = request.form.get("location")
        difficulty = request.form.get("difficulty")
        # duration = int(request.form.get("duration"))
        available_slots = int(request.form.get("available_slots"))
        description = request.form.get("description")
        status = request.form.get("status")
        assigned_staff_id = request.form.get("assigned_staff_id")
        start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d").date()
        end_date = datetime.strptime(request.form.get("end_date"), "%Y-%m-%d").date()
        trek.name = name

        
        if end_date < start_date:
            flash("End date cannot be earlier than start date.", "danger")
            return redirect(request.url)
        
        today = datetime.today().date()

        if start_date < today:
            flash("Start date cannot be before today.", "danger")
            return redirect(request.url)
        
        duration = (end_date - start_date).days + 1

        trek.location = location
        trek.difficulty = difficulty
        trek.duration = duration
        trek.start_date = start_date
        trek.end_date = end_date
        trek.available_slots = available_slots
        trek.description = description
        trek.status = status
        trek.assigned_staff_id = assigned_staff_id if assigned_staff_id else None

        db.session.commit()

        flash("Trek edited successfully!", "success")
        return redirect(url_for("admin.manage_treks"))
    
    
    return render_template("admin/trek_form.html",trek=trek,form=None,staff_options=staff_options)

@admin.route("/admin/treks/delete/<int:trek_id>", methods=["POST"])
def delete_trek(trek_id):
    if "user_id" not in session:
        return redirect(url_for("auth.home"))
    

    trek = models.Trek.query.get_or_404(trek_id)

    db.session.delete(trek)
    db.session.commit()

    flash("Trek deleted successfully!", "success")
    return redirect(url_for("admin.manage_treks"))


#                     //////////////////////////////////////////////////////////////////////////////////

@admin.route("/admin/bookings")
def manage_bookings():

    if "user_id" not in session:
        return redirect(url_for("auth.home"))
    

    bookings=models.Booking.query.all()
    return render_template("admin/bookings.html",bookings=bookings)

#                    /////////////////////////////////////////////////////////////////////////////////////////

@admin.route("/admin/users")
def manage_users():
    if "user_id" not in session:
        return redirect(url_for("auth.home"))
    
    user=models.User.query.filter_by(role=models.ROLE_TREKKER).all()
    return render_template("admin/users.html",user=user)

@admin.route("/admin/users/<int:user_id>/blacklist", methods=["POST"])
def blacklist_user(user_id):

    if "user_id" not in session:
        return redirect(url_for("auth.home"))
    
    user = models.User.query.get_or_404(user_id)

    user.blacklisted = True
    db.session.commit()

    flash("Trekker blacklisted successfully.", "success")
    return redirect(url_for("admin.manage_users"))



@admin.route("/admin/users/<int:user_id>/toggle-blacklist", methods=["POST"])
def toggle_blacklist_user(user_id):

    if "user_id" not in session:
        return redirect(url_for("auth.home"))

    user = models.User.query.get_or_404(user_id)

    if user.role == models.ROLE_ADMIN:
        flash("Admin account cannot be blacklisted.", "danger")
        return redirect(url_for("admin.manage_users"))

    user.blacklisted = not user.blacklisted

    db.session.commit()

    if user.blacklisted:
        flash(f"{user.full_name} has been blacklisted.", "success")
    else:
        flash(f"{user.full_name} has been reinstated.", "success")

    return redirect(url_for("admin.manage_users"))

#                    //////////////////////////////////////////////////////////////////////////////////////////

@admin.route("/admin/search")
def search():

    if "user_id" not in session:
        return redirect(url_for("auth.home"))
    

    q = request.args.get("q", "").strip()

    treks = []
    staff = []
    user = []

    if q:
        treks = models.Trek.query.filter(
            or_(
                models.Trek.name.ilike(f"%{q}%"),
                models.Trek.location.ilike(f"%{q}%")
            )
        ).all()

        staff = models.User.query.filter(
            models.User.role == models.ROLE_STAFF,
            or_(
                models.User.full_name.ilike(f"%{q}%"),
                models.User.email.ilike(f"%{q}%"),
                models.User.phone_number.ilike(f"%{q}%")
            )
        ).all()

        user = models.User.query.filter(
            models.User.role == models.ROLE_TREKKER,
            or_(
                models.User.full_name.ilike(f"%{q}%"),
                models.User.email.ilike(f"%{q}%"),
                models.User.phone_number.ilike(f"%{q}%")
            )
        ).all()

        
        if q.isdigit():
            id_num = int(q)

            treks += models.Trek.query.filter_by(id=id_num).all()

            staff += models.User.query.filter_by(
                id=id_num,
                role=models.ROLE_STAFF
            ).all()

            user += models.User.query.filter_by(
                id=id_num,
                role=models.ROLE_TREKKER
            ).all()

            # Remove duplicates
            treks = list({t.id: t for t in treks}.values())
            staff = list({s.id: s for s in staff}.values())
            user = list({u.id: u for u in user}.values())

    return render_template(
        "admin/search.html",
        q=q,
        treks=treks,
        staff=staff,
        user=user
    )





@admin.route("/admin/reports")
def reports():

    if "user_id" not in session:
        return redirect(url_for("auth.home"))
    
    

    total_treks = models.Trek.query.count()
    active_treks = models.Trek.query.filter_by(status="Active").count()
    completed_treks = models.Trek.query.filter_by(status="Completed").count()

    total_staff = models.User.query.filter_by(role=models.ROLE_STAFF).count()
    approved_staff = models.User.query.filter_by(
        role=models.ROLE_STAFF,
        approved=True,
        blacklisted=False
    ).count()

    pending_staff = models.User.query.filter_by(
        role=models.ROLE_STAFF,
        approved=False
    ).count()

    blacklisted_staff = models.User.query.filter_by(
        role=models.ROLE_STAFF,
        blacklisted=True
    ).count()

    total_users = models.User.query.filter_by(
        role=models.ROLE_TREKKER
    ).count()

    blacklisted_users = models.User.query.filter_by(
        role=models.ROLE_TREKKER,
        blacklisted=True
    ).count()

    total_bookings = models.Booking.query.count()

    booked = models.Booking.query.filter_by(status="Booked").count()
    cancelled = models.Booking.query.filter_by(status="Cancelled").count()
    completed = models.Booking.query.filter_by(status="Completed").count()


    recent_bookings = (
    models.Booking.query
    .order_by(models.Booking.booking_date.desc())
    .limit(5)
    .all()
    )

    return render_template(
        "admin/reports.html",

        total_treks=total_treks,
        active_treks=active_treks,
        completed_treks=completed_treks,

        total_staff=total_staff,
        approved_staff=approved_staff,
        pending_staff=pending_staff,
        blacklisted_staff=blacklisted_staff,

        total_users=total_users,
        blacklisted_users=blacklisted_users,

        total_bookings=total_bookings,
        booked=booked,
        cancelled=cancelled,
        completed=completed,
        recent_bookings=recent_bookings
    )