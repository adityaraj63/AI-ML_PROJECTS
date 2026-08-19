from flask import Blueprint, render_template
from flask_login import login_required
from models import Customer, Prediction

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    total_customers = Customer.query.count()
    total_predictions = Prediction.query.count()
    
    predicted_churn = Prediction.query.filter_by(prediction_result='Yes').count()
    
    # Active customers could be total customers minus those who churned (if we store ground truth churn, or if we use predicted churn)
    active_customers = Customer.query.filter_by(churn='No').count()
    if active_customers == 0:
        active_customers = total_customers - predicted_churn

    prediction_accuracy = 0
    # Can be updated from TrainingHistory if desired. Let's pass a placeholder or get from latest training
    
    recent_predictions = Prediction.query.order_by(Prediction.timestamp.desc()).limit(5).all()

    return render_template('dashboard/index.html',
                           total_customers=total_customers,
                           total_predictions=total_predictions,
                           predicted_churn=predicted_churn,
                           active_customers=active_customers,
                           recent_predictions=recent_predictions)
