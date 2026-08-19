import os
import pandas as pd
from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for
from flask_login import login_required
from models import db, Customer, Prediction
from ml.train_model import train_and_evaluate
from ml.predict import predict_churn

ml_bp = Blueprint('ml', __name__, url_prefix='/ml')

@ml_bp.route('/train', methods=['GET', 'POST'])
@login_required
def train():
    if request.method == 'POST':
        # Get all customer data from database
        customers = Customer.query.all()
        if not customers:
            flash('No customer data available to train the model.', 'danger')
            return redirect(url_for('ml.train'))
            
        data = []
        for c in customers:
            data.append({
                'gender': c.gender,
                'SeniorCitizen': c.senior_citizen,
                'Partner': c.partner,
                'Dependents': c.dependents,
                'tenure': c.tenure,
                'PhoneService': c.phone_service,
                'MultipleLines': c.multiple_lines,
                'InternetService': c.internet_service,
                'OnlineSecurity': c.online_security,
                'OnlineBackup': c.online_backup,
                'DeviceProtection': c.device_protection,
                'TechSupport': c.tech_support,
                'StreamingTV': c.streaming_tv,
                'StreamingMovies': c.streaming_movies,
                'Contract': c.contract,
                'PaperlessBilling': c.paperless_billing,
                'PaymentMethod': c.payment_method,
                'MonthlyCharges': c.monthly_charges,
                'TotalCharges': c.total_charges,
                'churn': c.churn
            })
            
        df = pd.DataFrame(data)
        
        try:
            metrics = train_and_evaluate(df, current_app.config['MODELS_FOLDER'], current_app.app_context())
            flash('Model trained successfully!', 'success')
            return render_template('ml/train_result.html', metrics=metrics)
        except Exception as e:
            flash(f'Error training model: {str(e)}', 'danger')
            return redirect(url_for('ml.train'))
            
    return render_template('ml/train.html')

@ml_bp.route('/predict_single', methods=['GET', 'POST'])
@login_required
def predict_single():
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        customer = Customer.query.filter_by(customer_id=customer_id).first()
        if not customer:
            flash('Customer not found.', 'danger')
            return redirect(url_for('ml.predict_single'))
            
        input_data = [{
            'gender': customer.gender,
            'SeniorCitizen': customer.senior_citizen,
            'Partner': customer.partner,
            'Dependents': customer.dependents,
            'tenure': customer.tenure,
            'PhoneService': customer.phone_service,
            'MultipleLines': customer.multiple_lines,
            'InternetService': customer.internet_service,
            'OnlineSecurity': customer.online_security,
            'OnlineBackup': customer.online_backup,
            'DeviceProtection': customer.device_protection,
            'TechSupport': customer.tech_support,
            'StreamingTV': customer.streaming_tv,
            'StreamingMovies': customer.streaming_movies,
            'Contract': customer.contract,
            'PaperlessBilling': customer.paperless_billing,
            'PaymentMethod': customer.payment_method,
            'MonthlyCharges': customer.monthly_charges,
            'TotalCharges': customer.total_charges,
        }]
        
        try:
            result = predict_churn(input_data, current_app.config['MODELS_FOLDER'])[0]
            
            # Save prediction to DB
            new_pred = Prediction(
                customer_db_id=customer.id,
                prediction_result=result['prediction'],
                probability=result['probability'],
                risk_level=result['risk_level']
            )
            db.session.add(new_pred)
            db.session.commit()
            
            flash('Prediction completed successfully.', 'success')
            return render_template('ml/predict.html', result=result, customer=customer)
        except Exception as e:
            flash(f'Error making prediction: {str(e)}', 'danger')
            
    # GET request - load customers for dropdown or search
    customers = Customer.query.limit(100).all()
    return render_template('ml/predict.html', customers=customers, result=None)

@ml_bp.route('/history')
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    filter_risk = request.args.get('risk', '')
    
    query = Prediction.query.join(Customer)
    if search:
        query = query.filter(Customer.customer_id.contains(search))
    if filter_risk:
        query = query.filter(Prediction.risk_level == filter_risk)
        
    pagination = query.order_by(Prediction.timestamp.desc()).paginate(page=page, per_page=15, error_out=False)
    predictions = pagination.items
    
    return render_template('history/predictions.html', predictions=predictions, pagination=pagination, search=search, filter_risk=filter_risk)

@ml_bp.route('/history/delete/<int:id>')
@login_required
def delete_prediction(id):
    pred = Prediction.query.get_or_404(id)
    db.session.delete(pred)
    db.session.commit()
    flash('Prediction record deleted.', 'success')
    return redirect(url_for('ml.history'))
