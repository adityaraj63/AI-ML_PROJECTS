# Customer Churn Prediction System

A complete production-ready AI/ML Full Stack Web Application to predict customer churn using the Telco Customer Churn Dataset. Built with Flask, Scikit-learn, Bootstrap 5, and SQLite.

## Features
- **Secure Authentication**: Admin login with password hashing.
- **SaaS Dashboard**: Interactive UI with Chart.js visualization.
- **Dataset Management**: Upload CSV, preview data, handle missing values automatically.
- **ML Pipeline**: Automated preprocessing (encoding, scaling), training Random Forest model.
- **Prediction**: Single customer prediction or bulk predictions with Risk Level analysis.
- **Reports**: Business summary and CSV export.

## Folder Structure
```text
CustomerChurnPrediction/
├── app.py                  # Main application entry point
├── config.py               # Configuration settings
├── models.py               # SQLAlchemy database models
├── create_admin.py         # Utility to create default admin
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── routes/                 # Flask Blueprints
├── templates/              # HTML Templates (Jinja2)
├── static/                 # CSS, JS, Images
├── ml/                     # ML scripts (train, predict, preprocess)
├── uploads/                # Directory for uploaded CSV datasets
├── dataset/                # Default dataset directory
```

## Installation Guide

### 1. Prerequisites
Ensure you have Python 3.8+ installed on your system.

### 2. Setup Virtual Environment (Optional but recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Database and Create Admin
```bash
python create_admin.py
```
*This will create the SQLite database (`database.db`) and seed the default admin credentials (`admin` / `admin123`).*

### 5. Run the Application
```bash
python app.py
```
The application will be available at `http://localhost:5000`

## Dataset
You can use the standard [Telco Customer Churn Dataset from Kaggle](https://www.kaggle.com/datasets/blastchar/telco-customer-churn).
1. Download the CSV.
2. Login to the application as `admin`.
3. Go to **Upload Dataset**, upload the CSV, and click **Import to Database**.
4. Go to **Train Model** to generate the Random Forest model.
5. Use the **Predict** page to analyze specific customers.
