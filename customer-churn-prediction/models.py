from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(50), unique=True, nullable=False)
    gender = db.Column(db.String(20))
    senior_citizen = db.Column(db.Integer)
    partner = db.Column(db.String(10))
    dependents = db.Column(db.String(10))
    tenure = db.Column(db.Integer)
    phone_service = db.Column(db.String(10))
    multiple_lines = db.Column(db.String(20))
    internet_service = db.Column(db.String(20))
    online_security = db.Column(db.String(20))
    online_backup = db.Column(db.String(20))
    device_protection = db.Column(db.String(20))
    tech_support = db.Column(db.String(20))
    streaming_tv = db.Column(db.String(20))
    streaming_movies = db.Column(db.String(20))
    contract = db.Column(db.String(20))
    paperless_billing = db.Column(db.String(10))
    payment_method = db.Column(db.String(50))
    monthly_charges = db.Column(db.Float)
    total_charges = db.Column(db.Float)
    churn = db.Column(db.String(10)) # Target
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    predictions = db.relationship('Prediction', backref='customer', cascade='all, delete-orphan')

class Prediction(db.Model):
    __tablename__ = 'predictions'
    id = db.Column(db.Integer, primary_key=True)
    customer_db_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    prediction_result = db.Column(db.String(10), nullable=False)
    probability = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False) # High, Medium, Low
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class TrainingHistory(db.Model):
    __tablename__ = 'training_history'
    id = db.Column(db.Integer, primary_key=True)
    accuracy = db.Column(db.Float)
    precision = db.Column(db.Float)
    recall = db.Column(db.Float)
    f1_score = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.utcnow)

class UploadedDataset(db.Model):
    __tablename__ = 'uploaded_datasets'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
