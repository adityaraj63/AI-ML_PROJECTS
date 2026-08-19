import csv
from io import StringIO
from flask import Blueprint, render_template, make_response
from flask_login import login_required
from models import Customer, Prediction

report_bp = Blueprint('report', __name__, url_prefix='/reports')

@report_bp.route('/summary')
@login_required
def summary():
    total_predictions = Prediction.query.count()
    total_churn_predicted = Prediction.query.filter_by(prediction_result='Yes').count()
    total_customers = Customer.query.count()
    total_churned_actual = Customer.query.filter_by(churn='Yes').count()
    
    retention_rate = 0
    if total_customers > 0:
        retention_rate = ((total_customers - total_churned_actual) / total_customers) * 100
        
    return render_template('reports/summary.html', 
                           total_predictions=total_predictions,
                           total_churn_predicted=total_churn_predicted,
                           retention_rate=round(retention_rate, 2))

@report_bp.route('/export_csv')
@login_required
def export_csv():
    predictions = Prediction.query.join(Customer).all()
    
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Prediction ID', 'Customer ID', 'Prediction Result', 'Probability', 'Risk Level', 'Timestamp'])
    
    for p in predictions:
        cw.writerow([p.id, p.customer.customer_id, p.prediction_result, p.probability, p.risk_level, p.timestamp.strftime('%Y-%m-%d %H:%M:%S')])
        
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=predictions_report.csv"
    output.headers["Content-type"] = "text/csv"
    return output
