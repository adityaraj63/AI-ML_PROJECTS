"""
=============================================================================
STEP 4: ANOMALY DETECTION (detect_anomalies.py)
=============================================================================
- Loads trained autoencoder model
- Loads calculated anomaly threshold from training stage
- Computes Reconstruction Error (MSE) for each record in the test set
- Compares MSE against Threshold:
    * MSE > Threshold  => ANOMALY (Label = 1)
    * MSE <= Threshold => NORMAL  (Label = 0)
- Prints count and percentage of detected anomalies
=============================================================================
"""

import os
import joblib
import numpy as np
from model import load_saved_model

def detect_anomalies():
    # ---------------------------------------------------------
    # 1. LOAD MODEL, THRESHOLD, AND TEST DATA
    # ---------------------------------------------------------
    model_path = 'autoencoder_model.h5'
    threshold_path = os.path.join('processed_data', 'threshold_data.pkl')
    test_path = os.path.join('processed_data', 'X_test.npy')
    
    model = load_saved_model(model_path)
    threshold_info = joblib.load(threshold_path)
    threshold = threshold_info['threshold']
    
    X_test = np.load(test_path)
    
    # ---------------------------------------------------------
    # 2. CALCULATE RECONSTRUCTION ERROR (MSE)
    # ---------------------------------------------------------
    predictions = model.predict(X_test)
    mse_errors = np.mean(np.square(X_test - predictions), axis=1)
    
    # ---------------------------------------------------------
    # 3. CLASSIFY RECORDS BASED ON THRESHOLD
    # ---------------------------------------------------------
    # 1 = Anomaly, 0 = Normal
    predicted_labels = (mse_errors > threshold).astype(int)
    
    num_total = len(predicted_labels)
    num_anomalies = np.sum(predicted_labels == 1)
    num_normal = np.sum(predicted_labels == 0)
    
    print("\n" + "="*50)
    print("ANOMALY DETECTION RESULTS")
    print("="*50)
    print(f"Total Test Records Processed : {num_total}")
    print(f"Decision Threshold (MSE)    : {threshold:.6f}")
    print(f"Detected Normal Records     : {num_normal} ({num_normal/num_total*100:.2f}%)")
    print(f"Detected Anomaly Records    : {num_anomalies} ({num_anomalies/num_total*100:.2f}%)")
    print("="*50 + "\n")
    
    # Save predictions and MSE errors for evaluation step
    np.save(os.path.join('processed_data', 'y_pred.npy'), predicted_labels)
    np.save(os.path.join('processed_data', 'mse_errors.npy'), mse_errors)
    
    return predicted_labels, mse_errors, threshold

if __name__ == "__main__":
    detect_anomalies()
