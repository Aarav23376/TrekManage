# TrekManage

A full-stack web application for managing trekking events with role-based access control. The system enables administrators to manage treks and users, staff members to conduct assigned treks, and trekkers to browse, book, and track their trekking activities.

Developed using Flask, SQLAlchemy, SQLite, Bootstrap, and Jinja2 following the MVC architecture.

---

## Features

### Administrator
- Secure authentication
- Dashboard with system statistics
- Create, edit, and delete treks
- Assign staff members to treks
- Manage users and staff
- View all bookings
- Search treks and users
- Generate management reports

### Trek Staff
- Secure login
- View assigned treks
- Manage only assigned treks
- Update available trek slots
- Open and close trek registrations
- Mark treks as Started and Completed
- View participant lists
- Update profile

### Trekker
- User registration and login
- Browse available treks
- Search and filter treks
- Book available treks
- Cancel bookings
- View booking history
- Track booking status
- Update profile

---

## Business Rules

- Role-based authorization
- Booking allowed only when trek status is Open
- Duplicate bookings are prevented
- Overbooking is prevented
- Only assigned staff members can manage their treks
- Trek completion automatically updates booking records
- Completed treks remain visible only to trekkers who participated

---

## Tech Stack

### Backend
- Python
- Flask
- SQLAlchemy ORM
- SQLite

### Frontend
- HTML5
- CSS3
- Bootstrap
- Jinja2 Templates

---

## Project Structure

```
TrekManage/
│
├── app/
│   ├── routes/
│   │   ├── auth.py
│   │   ├── admin.py
│   │   ├── staff.py
│   │   └── trekker.py
│   │
│   ├── templates/
│   ├── static/
│   ├── models.py
│   └── __init__.py
│
├── instance/
├── app.py
├── config.py
├── requirements.txt
└── README.md
```

---

## Installation

### Clone the repository

```bash
git clone https://github.com/<your-username>/TrekManage.git
cd TrekManage
```

### Create a virtual environment

Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the application

```bash
python app.py
```

The application will start on:

```
http://127.0.0.1:5000
```

---

## Project Highlights

- Multi-role authentication system
- Session-based authorization
- CRUD operations
- Trek booking workflow
- Trek lifecycle management
- Booking history tracking
- Search and filtering
- SQLAlchemy ORM relationships
- Responsive Bootstrap interface
- Modular Flask Blueprints architecture

---

## Future Improvements

- Email notifications
- Payment gateway integration
- Trek reviews and ratings
- Interactive maps
- Admin analytics dashboard
- REST API support

---

