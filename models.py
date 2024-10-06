from extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    routes = db.relationship('Route', backref='user', lazy=True)


class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    route_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    coordinates = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    distance = db.Column(db.Float, nullable=True)
    time = db.Column(db.String(50), nullable=True)
    addresses = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Route {self.route_name}>'
