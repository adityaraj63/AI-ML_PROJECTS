"""
=============================================================================
STEP 0: GENERATE / LOAD DATASET (generate_dataset.py)
=============================================================================
This script creates a realistic synthetic healthcare vitals dataset containing 
healthy normal measurements and a small percentage (~8%) of abnormal anomalies.

Vitals included:
- Heart Rate (bpm)
- Systolic Blood Pressure (mmHg)
- Diastolic Blood Pressure (mmHg)
- Oxygen Saturation / SpO2 (%)
- Body Temperature (°F)
- Blood Glucose Level (mg/dL)

Dataset Option Comparison for Viva:
1. Synthetic Healthcare Vitals Dataset (DEFAULT & RECOMMENDED):
   - 100% offline, lightweight, generates in seconds.
   - Features real human vital signs that are easy to explain in your viva.
2. MIT-BIH ECG Heartbeat Dataset:
   - Requires manual download from Kaggle (~500MB).
   - If mitbih_train.csv is placed in the 'data/' folder, the pipeline can process it too.
=============================================================================
"""

import os
import numpy as np
import pandas as pd

def generate_healthcare_vitals_dataset(num_samples=5000, anomaly_ratio=0.08, seed=42):
    """
    Generates synthetic healthcare vitals data with normal and anomaly samples.
    """
    np.random.seed(seed)
    
    num_anomalies = int(num_samples * anomaly_ratio)
    num_normal = num_samples - num_anomalies
    
    half_anomalies = num_anomalies // 2
    other_half_anomalies = num_anomalies - half_anomalies
    
    # ---------------------------------------------------------
    # 1. NORMAL HEALTHY DATA (Centered around normal ranges)
    # ---------------------------------------------------------
    normal_data = {
        'heart_rate': np.random.normal(loc=72, scale=6, size=num_normal),        # Normal: 60-85 bpm
        'systolic_bp': np.random.normal(loc=120, scale=7, size=num_normal),      # Normal: 110-130 mmHg
        'diastolic_bp': np.random.normal(loc=80, scale=5, size=num_normal),       # Normal: 70-85 mmHg
        'oxygen_saturation': np.clip(np.random.normal(loc=98, scale=1, size=num_normal), 95, 100), # Normal: 95-100%
        'body_temp': np.random.normal(loc=98.6, scale=0.4, size=num_normal),     # Normal: 97.8-99.2 °F
        'blood_glucose': np.random.normal(loc=100, scale=10, size=num_normal),   # Normal: 80-120 mg/dL
        'target': np.zeros(num_normal, dtype=int)                                # 0 = Normal
    }
    
    df_normal = pd.DataFrame(normal_data)
    
    # ---------------------------------------------------------
    # 2. ANOMALOUS DATA (Tachycardia, Hypoxia, High Fever, Hypoglycemia, Severe Hypertension)
    # ---------------------------------------------------------
    hr_anomalies = np.concatenate([
        np.random.normal(loc=145, scale=15, size=half_anomalies),  # Tachycardia (High HR)
        np.random.normal(loc=42, scale=5, size=other_half_anomalies)  # Bradycardia (Low HR)
    ])
    
    sys_anomalies = np.concatenate([
        np.random.normal(loc=185, scale=15, size=half_anomalies), # Severe Hypertension
        np.random.normal(loc=75, scale=8, size=other_half_anomalies)  # Severe Hypotension
    ])
    
    temp_anomalies = np.concatenate([
        np.random.normal(loc=103.5, scale=1.0, size=half_anomalies), # High Fever
        np.random.normal(loc=93.0, scale=1.0, size=other_half_anomalies)  # Hypothermia
    ])
    
    glucose_anomalies = np.concatenate([
        np.random.normal(loc=260, scale=30, size=half_anomalies), # Hyperglycemia
        np.random.normal(loc=45, scale=8, size=other_half_anomalies)  # Hypoglycemia
    ])
    
    anomaly_data = {
        'heart_rate': hr_anomalies,
        'systolic_bp': sys_anomalies,
        'diastolic_bp': np.random.normal(loc=110, scale=12, size=num_anomalies),
        'oxygen_saturation': np.clip(np.random.normal(loc=84, scale=5, size=num_anomalies), 70, 91), # Hypoxia (Low SpO2)
        'body_temp': temp_anomalies,
        'blood_glucose': glucose_anomalies,
        'target': np.ones(num_anomalies, dtype=int)                              # 1 = Anomaly
    }
    
    df_anomaly = pd.DataFrame(anomaly_data)
    
    # Combine and shuffle
    df_all = pd.concat([df_normal, df_anomaly], axis=0).sample(frac=1, random_state=seed).reset_index(drop=True)
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    output_path = os.path.join('data', 'healthcare_vitals.csv')
    df_all.to_csv(output_path, index=False)
    print(f"[SUCCESS] Healthcare Vitals dataset generated successfully at: {output_path}")
    print(f"Total samples: {len(df_all)} (Normal: {num_normal}, Anomalies: {num_anomalies})")
    
    # Also create a small sample CSV for Streamlit testing
    sample_upload = df_all.sample(n=20, random_state=100).drop(columns=['target'])
    sample_upload_path = os.path.join('data', 'sample_patient_upload.csv')
    sample_upload.to_csv(sample_upload_path, index=False)
    print(f"[SUCCESS] Sample patient upload file generated at: {sample_upload_path}\n")
    
    return df_all

if __name__ == "__main__":
    generate_healthcare_vitals_dataset()
