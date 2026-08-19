import os
import pandas as pd
from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for
from werkzeug.utils import secure_filename
from flask_login import login_required
from models import db, UploadedDataset, Customer

dataset_bp = Blueprint('dataset', __name__, url_prefix='/dataset')

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@dataset_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Save to database
            new_upload = UploadedDataset(filename=filename)
            db.session.add(new_upload)
            db.session.commit()
            
            flash('File successfully uploaded!', 'success')
            return redirect(url_for('dataset.preview', filename=filename))
            
    return render_template('dataset/upload.html')

@dataset_bp.route('/preview/<filename>')
@login_required
def preview(filename):
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        flash('File not found.', 'danger')
        return redirect(url_for('dataset.upload'))
        
    try:
        df = pd.read_csv(filepath)
        # Handle Missing Values briefly for preview
        df.replace(to_replace=" ", value=pd.NA, inplace=True)
        
        info = {
            'rows': df.shape[0],
            'columns': df.shape[1],
            'null_values': df.isnull().sum().sum(),
            'features': df.columns.tolist()
        }
        
        preview_data = df.head(10).to_html(classes='table table-striped table-hover', index=False)
        return render_template('dataset/preview.html', table=preview_data, info=info, filename=filename)
    except Exception as e:
        flash(f'Error reading CSV: {str(e)}', 'danger')
        return redirect(url_for('dataset.upload'))

@dataset_bp.route('/import/<filename>', methods=['POST'])
@login_required
def import_data(filename):
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        flash('File not found.', 'danger')
        return redirect(url_for('dataset.upload'))
        
    try:
        df = pd.read_csv(filepath)
        # Auto map to Customer model (Assuming Telco Churn format)
        df.columns = [c.lower().replace(' ', '_') for c in df.columns]
        
        # Handle TotalCharges missing
        df['totalcharges'] = pd.to_numeric(df['totalcharges'], errors='coerce')
        df['totalcharges'].fillna(0, inplace=True)

        added = 0
        for _, row in df.iterrows():
            if not Customer.query.filter_by(customer_id=str(row.get('customerid'))).first():
                customer = Customer(
                    customer_id=str(row.get('customerid')),
                    gender=str(row.get('gender')),
                    senior_citizen=int(row.get('seniorcitizen', 0)),
                    partner=str(row.get('partner')),
                    dependents=str(row.get('dependents')),
                    tenure=int(row.get('tenure', 0)),
                    phone_service=str(row.get('phoneservice')),
                    multiple_lines=str(row.get('multiplelines')),
                    internet_service=str(row.get('internetservice')),
                    online_security=str(row.get('onlinesecurity')),
                    online_backup=str(row.get('onlinebackup')),
                    device_protection=str(row.get('deviceprotection')),
                    tech_support=str(row.get('techsupport')),
                    streaming_tv=str(row.get('streamingtv')),
                    streaming_movies=str(row.get('streamingmovies')),
                    contract=str(row.get('contract')),
                    paperless_billing=str(row.get('paperlessbilling')),
                    payment_method=str(row.get('paymentmethod')),
                    monthly_charges=float(row.get('monthlycharges', 0)),
                    total_charges=float(row.get('totalcharges', 0)),
                    churn=str(row.get('churn', 'No'))
                )
                db.session.add(customer)
                added += 1
                
        db.session.commit()
        flash(f'Successfully imported {added} records to database.', 'success')
        return redirect(url_for('customer.list_customers'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error importing data: {str(e)}', 'danger')
        return redirect(url_for('dataset.preview', filename=filename))
