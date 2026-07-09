from app import models,db
from flask import render_template,request,session,flash
from flask import redirect,url_for
from werkzeug.security import check_password_hash,generate_password_hash
from datetime import datetime
from sqlalchemy import or_
from flask import Blueprint

trekker = Blueprint("trekker", __name__)

@trekker.route("/trekker/dashboard")
def trekker_dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.home"))

    current_user = models.User.query.get_or_404(session["user_id"])

    difficulty = request.args.get("difficulty", "")
    location = request.args.get("location", "")

    bookings = models.Booking.query.filter_by(
        user_id=current_user.id,
        status="Booked"
    ).all()

    treks = models.Trek.query.filter(models.Trek.status.in_(["Open", "Closed", "Completed"])).all()

    for booking in bookings:
        if booking.trek in treks:
            treks.remove(booking.trek)
    

    if difficulty:
        treks = treks.filter_by(difficulty=difficulty)

    if location:
        treks = treks.filter_by(location=location)

    treks = treks

    all_locations = (
        db.session.query(models.Trek.location)
        .distinct()
        .all()
    )

    all_locations = [loc[0] for loc in all_locations]

    my_bookings = (
        models.Booking.query
        .filter_by(user_id=current_user.id)
        .order_by(models.Booking.booking_date.desc()).order_by(models.Booking.id.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "trekker/dashboard.html",
        current_user=current_user,
        treks=treks,
        my_bookings=my_bookings,
        difficulty=difficulty,
        location=location,
        all_locations=all_locations
    )


#                                   //////////////////////////////////////////////////////////

@trekker.route("/trekker/trek/<int:trek_id>")
def trek_detail(trek_id):

    if "user_id" not in session:
        return redirect(url_for("auth.home"))

    current_user = models.User.query.get_or_404(session["user_id"])

    trek = models.Trek.query.get_or_404(trek_id)

    existing_booking = models.Booking.query.filter(
    models.Booking.user_id == current_user.id,
    models.Booking.trek_id == trek.id,
    models.Booking.status != "Cancelled"
    ).first()

    return render_template(
        "trekker/trek_detail.html",
        trek=trek,
        existing_booking=existing_booking
    )



#                                       //////////////////////////////////////////////////////////////////////

@trekker.route("/trekker/browse")
def browse_treks():

    if "user_id" not in session:
        return redirect(url_for("auth.home"))

    current_user = models.User.query.get(session["user_id"])

    q = request.args.get("q", "").strip()
    difficulty = request.args.get("difficulty", "")
    location = request.args.get("location", "")

    treks = models.Trek.query.filter(
        models.Trek.status.in_(["Open", "Closed", "Completed"])
    )

    if q:
        treks = treks.filter(
            or_(
                models.Trek.name.ilike(f"%{q}%"),
                models.Trek.location.ilike(f"%{q}%")
            )
        )

    if difficulty:
        treks = treks.filter_by(difficulty=difficulty)

    if location:
        treks = treks.filter_by(location=location)

    treks = treks.order_by(models.Trek.start_date).all()

    filtered_treks = []

    for trek in treks:
        if trek.status != "Completed":
            filtered_treks.append(trek)
        else:
            booking = models.Booking.query.filter_by(
                user_id=current_user.id,
                trek_id=trek.id
            ).first()

            if booking:
                filtered_treks.append(trek)

    all_locations = (
        db.session.query(models.Trek.location)
        .distinct()
        .all()
    )

    all_locations = [loc[0] for loc in all_locations]

    return render_template(
        "trekker/browse.html",
        treks=filtered_treks,
        q=q,
        difficulty=difficulty,
        location=location,
        all_locations=all_locations
    )




#                                        ///////////////////////////////////////////////////////////////////////


@trekker.route("/trekker/book/<int:trek_id>", methods=["POST"])
def book_trek(trek_id):

    if "user_id" not in session:
        return redirect(url_for("auth.home"))

    current_user = models.User.query.get_or_404(session["user_id"])

    trek = models.Trek.query.get_or_404(trek_id)

    
    if trek.status != "Open":
        flash("This trek is not open for booking.", "warning")
        return redirect(url_for("trekker.trek_detail", trek_id=trek.id))

   
    if trek.available_slots <= 0:
        flash("No slots available.", "danger")
        return redirect(url_for("trekker.trek_detail", trek_id=trek.id))


    existing = models.Booking.query.filter(
        models.Booking.user_id == current_user.id,
        models.Booking.trek_id == trek.id,
        models.Booking.status != "Cancelled"
    ).first()

    if existing:
        flash("You have already booked this trek.", "warning")
        return redirect(url_for("trekker.trek_detail", trek_id=trek.id))
    
    today = datetime.today().date()

    if trek.start_date < today:
        flash("Booking is closed because this trek has already started.", "danger")
        return redirect(url_for("trekker.trek_detail", trek_id=trek.id))

    booking = models.Booking(
        user_id=current_user.id,
        trek_id=trek.id,
        status="Booked"
    )

    db.session.add(booking)

    trek.available_slots -= 1

    db.session.commit()

    flash("Trek booked successfully!", "success")

    return redirect(url_for("trekker.my_bookings"))

#                                      /////////////////////////////////////////////////////////////////

@trekker.route("/trekker/my-bookings")
def my_bookings():

    if "user_id" not in session:
        return redirect(url_for("auth.home"))

    bookings = (
        models.Booking.query
        .filter_by(user_id=session["user_id"])
        .order_by(models.Booking.booking_date.desc()).order_by(models.Booking.id.desc())
        .all()
    )

    return render_template(
        "trekker/bookings.html",
        bookings=bookings
    )


#                                       ///////////////////////////////////////////////////////////////////////////


@trekker.route("/trekker/cancel-booking/<int:booking_id>", methods=["POST"])
def cancel_booking(booking_id):

    if "user_id" not in session:
        return redirect(url_for("auth.home"))

    booking = models.Booking.query.get_or_404(booking_id)

    
    if booking.user_id != session["user_id"]:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("trekker.my_bookings"))


    if booking.status == "Cancelled":
        flash("This booking is already cancelled.", "warning")
        return redirect(url_for("trekker.my_bookings"))

    booking.status = "Cancelled"

    booking.trek.available_slots += 1

    db.session.commit()

    flash("Booking cancelled successfully.", "success")

    return redirect(url_for("trekker.my_bookings"))




#                                          /////////////////////////////////////////////////////////////////

@trekker.route("/trekker/history")
def history():

    if "user_id" not in session:
        return redirect(url_for("auth.home"))

    bookings = (
        models.Booking.query
        .filter_by(
            user_id=session["user_id"],
            status="Completed"
        )
        .all()
    )

    return render_template(
        "trekker/history.html",
        bookings=bookings
    )
#                                               //////////////////////////////////////////////////////

@trekker.route("/trekker/profile", methods=["GET", "POST"])
def profile():

    if "user_id" not in session:
        return redirect(url_for("auth.home"))

    current_user = models.User.query.get_or_404(session["user_id"])

    if request.method == "POST":

        current_user.full_name = request.form.get("name")
        current_user.phone_number = request.form.get("contact")

        db.session.commit()

        flash("Profile updated successfully.", "success")

        return redirect(url_for("trekker.profile"))

    return render_template(
        "trekker/profile.html",
        current_user=current_user
    )