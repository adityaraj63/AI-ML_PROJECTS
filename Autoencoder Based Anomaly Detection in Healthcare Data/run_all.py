"""
=============================================================================
MASTER PIPELINE RUNNER (run_all.py)
=============================================================================
Runs the complete Autoencoder Anomaly Detection pipeline end-to-end:
  Step 0: Generate / Check Dataset (generate_dataset.py)
  Step 1: Preprocess Data & Normalization (data_preprocessing.py)
  Step 2: Define Autoencoder Architecture (model.py)
  Step 3: Train Model on Normal Data (train.py)
  Step 4: Detect Anomalies with Threshold (detect_anomalies.py)
  Step 5: Calculate Metrics & Generate Plots (evaluate.py)
=============================================================================
"""

import time
from generate_dataset import generate_healthcare_vitals_dataset
from data_preprocessing import load_and_preprocess_data
from train import train_model
from detect_anomalies import detect_anomalies
from evaluate import evaluate_performance

def main():
    print("="*70)
    print(" STARTING AUTOENCODER HEALTHCARE ANOMALY DETECTION PIPELINE")
    print("="*70 + "\n")
    
    start_time = time.time()
    
    # Step 0: Generate Dataset
    print("[STEP 0/5] Dataset Check / Generation...")
    generate_healthcare_vitals_dataset()
    
    # Step 1: Preprocess Data
    print("[STEP 1/5] Preprocessing & Normalizing Data...")
    load_and_preprocess_data()
    
    # Step 2 & 3: Model Architecture & Training
    print("[STEP 2 & 3/5] Building & Training Autoencoder Model...")
    train_model(epochs=50, batch_size=32)
    
    # Step 4: Anomaly Detection
    print("[STEP 4/5] Running Anomaly Detection...")
    detect_anomalies()
    
    # Step 5: Evaluation & Plotting
    print("[STEP 5/5] Calculating Metrics & Saving Plots...")
    evaluate_performance()
    
    elapsed_time = time.time() - start_time
    print("="*70)
    print(f" PIPELINE COMPLETED SUCCESSFULLY IN {elapsed_time:.2f} SECONDS!")
    print("Saved Outputs:")
    print("  - autoencoder_model.h5 / .pkl (Trained Autoencoder Model)")
    print("  - loss_curve.png (Training vs Validation Loss Plot)")
    print("  - reconstruction_error_dist.png (MSE Error Distribution Plot)")
    print("  - confusion_matrix.png (Confusion Matrix Heatmap)")
    print("  - roc_curve.png (ROC Curve & AUC Score)")
    print("\nTo launch the interactive web dashboard, run:")
    print("  streamlit run app.py")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
