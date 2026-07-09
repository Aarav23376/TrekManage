from app import models,db
from flask import render_template,request,session,flash
from flask import redirect,url_for
from werkzeug.security import check_password_hash,generate_password_hash
from datetime import datetime
from sqlalchemy import or_
from flask import Blueprint

staff = Blueprint("staff", __name__)

@staff.route("/staff/dashboard")
def staff_dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.home"))

    current_staff = models.User.query.get(session["user_id"])

    my_treks = models.Trek.query.filter_by(assigned_staff_id=current_staff.id).all()

    total_participants = 0
    open_treks = 0

    for trek in my_treks:

        active_booking_count = models.Booking.query.filter_by(
            trek_id=trek.id,
            status="Booked"
        ).count()

        trek.active_booking_count = active_booking_count

        total_participants += active_booking_count

        if trek.status == "Open":
            open_treks += 1

    return render_template(
        "staff/dashboard.html",
        my_treks=my_treks,
        total_participants=total_participants,
        open_treks=open_treks
    )
#                                       ////////////////////////////////////////////////////////////////


@staff.route("/my-treks")
def my_treks():

    if "user_id" not in session:
        return redirect(url_for("auth.home"))

    my_treks = models.Trek.query.filter_by(
        assigned_staff_id=session["user_id"]
    ).order_by(models.Trek.start_date).all()

    for trek in my_treks:
        trek.active_booking_count = models.Booking.query.filter_by(
            trek_id=trek.id,
            status="Booked"
        ).count()

    return render_template(
        "staff/my_treks.html",
        my_treks=my_treks
    )



#                                           ////////////////////////////////////////////////////////////////////////


@staff.route("/staff/trek/<int:trek_id>")
def trek_detail(trek_id):

    if "user_id" not in session:
        return redirect(url_for("auth.home"))

    trek = models.Trek.query.get_or_404(trek_id)

    if trek.assigned_staff_id != session["user_id"]:
        flash("You are not authorized to view this trek.", "danger")
        return redirect(url_for("staff.staff_dashboard"))

    participants = models.Booking.query.filter_by(
        trek_id=trek.id
    ).all()

    trek.active_booking_count = models.Booking.query.filter_by(
        trek_id=trek.id,
        status="Booked"
    ).count()

    return render_template(
        "staff/trek_detail.html",
        trek=trek,
        participants=participants
    )

#                                               ///////////////////////////////////////////////////////////



@staff.route("/staff/profile", methods=["GET", "POST"])
def profile():

    if "user_id" not in session:
        return redirect(url_for("auth.home"))

    current_user = models.User.query.get_or_404(session["user_id"])

    if request.method == "POST":

        current_user.full_name = request.form.get("name")
        current_user.phone_number = request.form.get("contact")

        db.session.commit()

        flash("Profile updated successfully.", "success")

        return redirect(url_for("staff.profile"))

    return render_template(
        "staff/profile.html",
        current_user=current_user
    )


#                                               ///////////////////////////////////////////////////////////



@staff.route("/staff/trek/<int:trek_id>/update", methods=["POST"])
def update_trek(trek_id):

    if "user_id" not in session:
        return redirect(url_for("auth.home"))

    trek = models.Trek.query.get_or_404(trek_id)

    if trek.assigned_staff_id != session["user_id"]:
        flash("Unauthorized.", "danger")
        return redirect(url_for("staff.staff_dashboard"))

    trek.available_slots = int(request.form.get("available_slots"))

    status = request.form.get("status")

    if status is not None:
        trek.status = status


    db.session.commit()

    flash("Trek updated successfully.", "success")

    return redirect(url_for("staff.trek_detail", trek_id=trek.id))

#                                               /////////////////////////////////////////////////////////////////


@staff.route("/staff/trek/<int:trek_id>/start", methods=["POST"])
def mark_started(trek_id):

    if "user_id" not in session:
        return redirect(url_for("auth.home"))

    trek = models.Trek.query.get_or_404(trek_id)

    if trek.status != "Open":
        flash("Only open treks can be started.", "danger")
        return redirect(url_for("staff.trek_detail", trek_id=trek.id))

    if trek.assigned_staff_id != session["user_id"]:
        flash("Unauthorized.", "danger")
        return redirect(url_for("staff.staff_dashboard"))

    trek.status = "Closed"

    db.session.commit()

    flash("Trek marked as started.", "success")

    return redirect(url_for("staff.trek_detail", trek_id=trek.id))


@staff.route("/staff/trek/<int:trek_id>/complete", methods=["POST"])
def mark_completed(trek_id):

    if "user_id" not in session:
        return redirect(url_for("auth.home"))

    trek = models.Trek.query.get_or_404(trek_id)

    if trek.assigned_staff_id != session["user_id"]:
        flash("Unauthorized.", "danger")
        return redirect(url_for("staff.staff_dashboard"))
    
    if trek.status == "Completed":
        flash("Trek is already completed.", "warning")
        return redirect(url_for("staff.trek_detail", trek_id=trek.id))

    trek.status = "Completed"

    models.Booking.query.filter_by(
        trek_id=trek.id,
        status="Booked"
    ).update({"status": "Completed"})

    db.session.commit()

    flash("Trek marked as completed.", "success")

    return redirect(url_for("staff.trek_detail", trek_id=trek.id))



