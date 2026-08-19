import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib
import os

def preprocess_data(df, save_path):
    """
    Preprocess the Telco Churn DataFrame.
    """
    df = df.copy()
    
    # Handle missing values
    if 'TotalCharges' in df.columns:
        df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
        df['TotalCharges'].fillna(0, inplace=True)
    
    if 'total_charges' in df.columns:
        df['total_charges'] = pd.to_numeric(df['total_charges'], errors='coerce')
        df['total_charges'].fillna(0, inplace=True)

    # Drop customerID if exists
    if 'customerID' in df.columns:
        df.drop('customerID', axis=1, inplace=True)
    if 'customer_id' in df.columns:
        df.drop('customer_id', axis=1, inplace=True)
    if 'id' in df.columns:
        df.drop('id', axis=1, inplace=True)
    if 'created_at' in df.columns:
        df.drop('created_at', axis=1, inplace=True)

    # Separate features and target
    target_col = 'churn' if 'churn' in df.columns else 'Churn'
    
    if target_col in df.columns:
        y = df[target_col].map({'Yes': 1, 'No': 0, '1': 1, '0': 0})
        X = df.drop(target_col, axis=1)
    else:
        y = None
        X = df
        
    encoders = {}
    scaler = StandardScaler()
    
    cat_cols = X.select_dtypes(include=['object']).columns
    num_cols = X.select_dtypes(include=['int64', 'float64']).columns
    
    for col in cat_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        encoders[col] = le
        
    if len(num_cols) > 0:
        X[num_cols] = scaler.fit_transform(X[num_cols])
        
    encoders['scaler'] = scaler
    encoders['num_cols'] = list(num_cols)
    encoders['cat_cols'] = list(cat_cols)
    encoders['features'] = list(X.columns)

    # Save encoders
    os.makedirs(save_path, exist_ok=True)
    joblib.dump(encoders, os.path.join(save_path, 'encoders.pkl'))
    
    return X, y, encoders

def preprocess_input(input_data, encoders_path):
    """
    Preprocess single or bulk prediction input.
    """
    df = pd.DataFrame(input_data)
    encoders = joblib.load(os.path.join(encoders_path, 'encoders.pkl'))
    
    if 'customerID' in df.columns:
        df.drop('customerID', axis=1, inplace=True)
    if 'customer_id' in df.columns:
        df.drop('customer_id', axis=1, inplace=True)
    if 'id' in df.columns:
        df.drop('id', axis=1, inplace=True)
        
    if 'TotalCharges' in df.columns:
        df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce').fillna(0)
    if 'total_charges' in df.columns:
        df['total_charges'] = pd.to_numeric(df['total_charges'], errors='coerce').fillna(0)

    # Reorder columns to match training
    expected_cols = encoders['features']
    for col in expected_cols:
        if col not in df.columns:
            df[col] = 0 # Dummy value if missing

    df = df[expected_cols]

    for col in encoders['cat_cols']:
        if col in df.columns:
            # handle unseen labels
            le = encoders[col]
            df[col] = df[col].astype(str).apply(lambda x: x if x in le.classes_ else le.classes_[0])
            df[col] = le.transform(df[col])
            
    if len(encoders['num_cols']) > 0:
        scaler = encoders['scaler']
        df[encoders['num_cols']] = scaler.transform(df[encoders['num_cols']])
        
    return df
