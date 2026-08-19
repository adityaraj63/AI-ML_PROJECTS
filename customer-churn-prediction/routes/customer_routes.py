from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import db, Customer

customer_bp = Blueprint('customer', __name__, url_prefix='/customers')

@customer_bp.route('/')
@login_required
def list_customers():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Customer.query
    if search:
        query = query.filter(Customer.customer_id.contains(search) | Customer.payment_method.contains(search))
        
    pagination = query.order_by(Customer.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    customers = pagination.items
    
    return render_template('customers/list.html', customers=customers, pagination=pagination, search=search)

@customer_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    if request.method == 'POST':
        # Get data from form
        new_customer = Customer(
            customer_id=request.form.get('customer_id'),
            gender=request.form.get('gender'),
            senior_citizen=int(request.form.get('senior_citizen', 0)),
            partner=request.form.get('partner'),
            dependents=request.form.get('dependents'),
            tenure=int(request.form.get('tenure', 0)),
            phone_service=request.form.get('phone_service'),
            multiple_lines=request.form.get('multiple_lines'),
            internet_service=request.form.get('internet_service'),
            online_security=request.form.get('online_security'),
            online_backup=request.form.get('online_backup'),
            device_protection=request.form.get('device_protection'),
            tech_support=request.form.get('tech_support'),
            streaming_tv=request.form.get('streaming_tv'),
            streaming_movies=request.form.get('streaming_movies'),
            contract=request.form.get('contract'),
            paperless_billing=request.form.get('paperless_billing'),
            payment_method=request.form.get('payment_method'),
            monthly_charges=float(request.form.get('monthly_charges', 0.0)),
            total_charges=float(request.form.get('total_charges', 0.0) or 0.0),
            churn=request.form.get('churn', 'No')
        )
        db.session.add(new_customer)
        try:
            db.session.commit()
            flash('Customer added successfully!', 'success')
            return redirect(url_for('customer.list_customers'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding customer: {str(e)}', 'danger')
            
    return render_template('customers/profile.html', customer=None, action='Add')

@customer_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    if request.method == 'POST':
        customer.customer_id = request.form.get('customer_id')
        customer.gender = request.form.get('gender')
        customer.senior_citizen = int(request.form.get('senior_citizen', 0))
        customer.partner = request.form.get('partner')
        customer.dependents = request.form.get('dependents')
        customer.tenure = int(request.form.get('tenure', 0))
        customer.phone_service = request.form.get('phone_service')
        customer.multiple_lines = request.form.get('multiple_lines')
        customer.internet_service = request.form.get('internet_service')
        customer.online_security = request.form.get('online_security')
        customer.online_backup = request.form.get('online_backup')
        customer.device_protection = request.form.get('device_protection')
        customer.tech_support = request.form.get('tech_support')
        customer.streaming_tv = request.form.get('streaming_tv')
        customer.streaming_movies = request.form.get('streaming_movies')
        customer.contract = request.form.get('contract')
        customer.paperless_billing = request.form.get('paperless_billing')
        customer.payment_method = request.form.get('payment_method')
        customer.monthly_charges = float(request.form.get('monthly_charges', 0.0))
        customer.total_charges = float(request.form.get('total_charges', 0.0) or 0.0)
        customer.churn = request.form.get('churn', 'No')

        try:
            db.session.commit()
            flash('Customer updated successfully!', 'success')
            return redirect(url_for('customer.list_customers'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating customer: {str(e)}', 'danger')

    return render_template('customers/profile.html', customer=customer, action='Edit')

@customer_bp.route('/delete/<int:id>')
@login_required
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    flash('Customer deleted successfully.', 'success')
    return redirect(url_for('customer.list_customers'))

@customer_bp.route('/view/<int:id>')
@login_required
def view_customer(id):
    customer = Customer.query.get_or_404(id)
    return render_template('customers/profile.html', customer=customer, action='View')
