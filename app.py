# app.py
import json
import os

from flask import Flask, render_template, request, redirect, session, url_for, flash

from extensions import db
from models import User, Route

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'wanderphilly.db')
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_ECHO'] = True

db.init_app(app)


# Home route
@app.route('/')
def home():
    return render_template('base.html')


# User registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists! Please choose a different one.')
            return redirect(url_for('register'))

        # Create a new user and add to the database
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        # Log the user in by saving their ID in the session
        session['user_id'] = new_user.id
        flash('Registration successful! You are now logged in.')
        return redirect(url_for('home'))

    return render_template('register.html')


# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']

        # Find the user in the database
        user = User.query.filter_by(username=username).first()

        # Check if user exists and password matches
        if user and user.password == password:
            session['user_id'] = user.id
            # flash('Login successful!')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials! Please try again.')
            return redirect(url_for('login'))

    return render_template('login.html')


# Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)


# Route upload route
@app.route('/upload', methods=['GET', 'POST'])
def upload_route():
    if 'user_id' not in session:
        flash('Please log in to upload a route.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        route_name = request.form.get('route_name')
        description = request.form.get('description')
        rating = request.form.get('rating')
        coordinates_json = request.form.get('route_data')
        tags_json = request.form.get('selected_tags')
        distance = request.form.get('distance')
        time_estimate = request.form.get('time')
        addresses_json = request.form.get('addresses')

        try:
            coordinates = json.loads(coordinates_json)
            tags = json.loads(tags_json)
            addresses = json.loads(addresses_json)
            distance = float(distance) if distance else None
            time_estimate = str(time_estimate) if time_estimate else None
        except (TypeError, json.JSONDecodeError, ValueError):
            # flash('Invalid route data, tags, distance, time, or addresses.')
            return redirect(url_for('upload_route'))

        if not route_name or not description or not rating or not coordinates or not tags:
            # flash('Please fill out all required fields.')
            return redirect(url_for('upload_route'))

        if len(coordinates) < 2:
            # flash('Please select at least two points on the map to create a route.')
            return redirect(url_for('upload_route'))

        new_route = Route(
            user_id=session['user_id'],
            route_name=route_name,
            description=description,
            coordinates=json.dumps(coordinates),
            tags=','.join(tags),
            rating=int(rating),
            distance=distance,
            time=time_estimate,
            addresses=json.dumps(addresses)
        )
        db.session.add(new_route)
        db.session.commit()

        # flash('Route uploaded successfully!')
        return redirect(url_for('view_routes'))

    return render_template('upload.html')

@app.route('/view_routes')
def view_routes():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Fetch all routes from the database
    routes = Route.query.all()

    # Parse JSON fields for each route
    for route in routes:
        # Parse coordinates
        try:
            route.coordinates = json.loads(route.coordinates)
        except (TypeError, json.JSONDecodeError):
            route.coordinates = []

        # Parse addresses
        try:
            route.addresses = json.loads(route.addresses)
        except (TypeError, json.JSONDecodeError):
            route.addresses = []

    return render_template('view_routes.html', routes=routes)

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.')
    return redirect(url_for('home'))


# Testing database connection
@app.route('/test_db')
def test_db():
    try:
        # Run a simple query to check connection
        user_count = db.session.query(User).count()
        return f"Connected to the database! User count: {user_count}"
    except Exception as e:
        return f"Failed to connect to the database: {str(e)}"


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
