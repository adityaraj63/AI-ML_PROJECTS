"""
=============================================================================
STEP 1: DATA PREPROCESSING (data_preprocessing.py)
=============================================================================
- Loads dataset (Healthcare vitals or MIT-BIH ECG dataset)
- Handles missing values
- Normalizes features using MinMaxScaler (scales feature range to [0, 1])
- Splits data into:
    1. Training set: NORMAL data ONLY (for autoencoder to learn normal patterns)
    2. Validation set: NORMAL data ONLY (for setting anomaly threshold)
    3. Test set: MIXED data (Normal + Anomalies for testing detection accuracy)
- Prints detailed dataset statistics
=============================================================================
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from generate_dataset import generate_healthcare_vitals_dataset

def load_and_preprocess_data():
    vitals_file = os.path.join('data', 'healthcare_vitals.csv')
    mitbih_file = os.path.join('data', 'mitbih_train.csv')
    
    # ---------------------------------------------------------
    # 1. LOAD DATASET (Fallback logic for offline / Kaggle)
    # ---------------------------------------------------------
    if os.path.exists(mitbih_file):
        print(f"[INFO] Found MIT-BIH dataset at '{mitbih_file}'. Loading MIT-BIH...")
        df = pd.read_csv(mitbih_file, header=None)
        # Last column is target class (0 = Normal, 1-4 = Abnormal)
        target_col = df.columns[-1]
        df[target_col] = (df[target_col] != 0).astype(int) # 0 = Normal, 1 = Anomaly
        feature_cols = [c for c in df.columns if c != target_col]
        dataset_name = "MIT-BIH ECG Dataset"
    elif os.path.exists(vitals_file):
        print(f"[INFO] Loading Healthcare Vitals dataset from '{vitals_file}'...")
        df = pd.read_csv(vitals_file)
        target_col = 'target'
        feature_cols = [c for c in df.columns if c != target_col]
        dataset_name = "Healthcare Vitals Dataset"
    else:
        print("[INFO] No dataset found. Auto-generating synthetic Healthcare Vitals dataset...")
        df = generate_healthcare_vitals_dataset()
        target_col = 'target'
        feature_cols = [c for c in df.columns if c != target_col]
        dataset_name = "Healthcare Vitals Dataset"

    # ---------------------------------------------------------
    # 2. HANDLE MISSING VALUES
    # ---------------------------------------------------------
    if df.isnull().sum().sum() > 0:
        print("[INFO] Found missing values. Filling missing values with column means...")
        df = df.fillna(df.mean())
    else:
        print("[INFO] No missing values found in dataset.")

    # ---------------------------------------------------------
    # 3. SEPARATE NORMAL AND ANOMALY SAMPLES
    # ---------------------------------------------------------
    normal_df = df[df[target_col] == 0].reset_index(drop=True)
    anomaly_df = df[df[target_col] == 1].reset_index(drop=True)
    
    print("\n" + "="*50)
    print(f"DATASET STATISTICS ({dataset_name})")
    print("="*50)
    print(f"Total Dataset Shape : {df.shape}")
    print(f"Total Normal Count  : {len(normal_df)} ({len(normal_df)/len(df)*100:.2f}%)")
    print(f"Total Anomaly Count : {len(anomaly_df)} ({len(anomaly_df)/len(df)*100:.2f}%)")
    print("="*50 + "\n")

    # ---------------------------------------------------------
    # 4. SPLIT NORMAL DATA FOR TRAIN, VAL, TEST
    # Autoencoder trains ONLY on normal data!
    # ---------------------------------------------------------
    # Split normal data: 70% train, 15% val, 15% test
    normal_train, normal_temp = train_test_split(normal_df, test_size=0.30, random_state=42)
    normal_val, normal_test = train_test_split(normal_temp, test_size=0.50, random_state=42)

    # Combine normal_test with ALL anomaly samples to create a balanced mixed test set
    mixed_test_df = pd.concat([normal_test, anomaly_df], axis=0).sample(frac=1, random_state=42).reset_index(drop=True)

    X_train_raw = normal_train[feature_cols].values
    X_val_raw = normal_val[feature_cols].values
    X_test_raw = mixed_test_df[feature_cols].values
    y_test = mixed_test_df[target_col].values

    # ---------------------------------------------------------
    # 5. FEATURE NORMALIZATION (MinMaxScaler)
    # ---------------------------------------------------------
    scaler = MinMaxScaler()
    # Fit scaler ONLY on training data to prevent data leakage
    X_train_scaled = scaler.fit_transform(X_train_raw)
    X_val_scaled = scaler.transform(X_val_raw)
    X_test_scaled = scaler.transform(X_test_raw)

    print(f"Normal Training Shape   : {X_train_scaled.shape}")
    print(f"Normal Validation Shape : {X_val_scaled.shape}")
    print(f"Mixed Test Set Shape    : {X_test_scaled.shape}")
    print(f"Test Class Distribution : Normal={np.sum(y_test==0)}, Anomaly={np.sum(y_test==1)}")

    # ---------------------------------------------------------
    # 6. SAVE PROCESSED ARTIFACTS
    # ---------------------------------------------------------
    os.makedirs('processed_data', exist_ok=True)
    
    np.save(os.path.join('processed_data', 'X_train_normal.npy'), X_train_scaled)
    np.save(os.path.join('processed_data', 'X_val_normal.npy'), X_val_scaled)
    np.save(os.path.join('processed_data', 'X_test.npy'), X_test_scaled)
    np.save(os.path.join('processed_data', 'y_test.npy'), y_test)
    
    joblib.dump(scaler, os.path.join('processed_data', 'scaler.pkl'))
    joblib.dump(feature_cols, os.path.join('processed_data', 'feature_cols.pkl'))
    
    print("\n[SUCCESS] Preprocessing complete! Processed files saved in 'processed_data/'\n")

if __name__ == "__main__":
    load_and_preprocess_data()
