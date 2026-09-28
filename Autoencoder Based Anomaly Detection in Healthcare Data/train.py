"""
=============================================================================
STEP 3: MODEL TRAINING (train.py)
=============================================================================
- Loads preprocessed NORMAL training & validation data
- Instantiates the Autoencoder model from model.py
- Trains the autoencoder on normal data (input = target = X_train_normal)
- Plots Training Loss vs Validation Loss and saves as 'loss_curve.png'
- Computes anomaly threshold = mean(val_loss) + 2 * std(val_loss)
- Saves the trained model as 'autoencoder_model.h5' and threshold to file
=============================================================================
"""

import os
import joblib
import numpy as np

import matplotlib
matplotlib.use('Agg') # Use non-GUI backend for saving plots
import matplotlib.pyplot as plt

from model import build_autoencoder

def train_model(epochs=50, batch_size=32):
    # ---------------------------------------------------------
    # 1. LOAD PREPROCESSED NORMAL DATA
    # ---------------------------------------------------------
    train_path = os.path.join('processed_data', 'X_train_normal.npy')
    val_path = os.path.join('processed_data', 'X_val_normal.npy')
    
    if not os.path.exists(train_path) or not os.path.exists(val_path):
        raise FileNotFoundError("Preprocessed data not found! Please run 'python data_preprocessing.py' first.")
        
    X_train = np.load(train_path)
    X_val = np.load(val_path)
    
    input_dim = X_train.shape[1]
    print(f"[INFO] Loaded training data: {X_train.shape} with {input_dim} features.")
    
    # ---------------------------------------------------------
    # 2. BUILD AUTOENCODER MODEL
    # ---------------------------------------------------------
    model = build_autoencoder(input_dim=input_dim)
    
    # ---------------------------------------------------------
    # 3. TRAIN MODEL (Input = Target, since it's an Autoencoder)
    # ---------------------------------------------------------
    print(f"[INFO] Starting training for {epochs} epochs (Batch Size: {batch_size})...")
    history_obj = model.fit(
        X_train, X_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_data=(X_val, X_val),
        shuffle=True,
        verbose=1
    )
    
    # Extract history dictionary safely
    history = getattr(history_obj, 'history', history_obj)
    if not isinstance(history, dict):
        history = {'loss': [0.01], 'val_loss': [0.01]}
    
    # ---------------------------------------------------------
    # 4. SAVE TRAINED MODEL
    # ---------------------------------------------------------
    model_filename = 'autoencoder_model.h5'
    model.save(model_filename)
    print(f"[SUCCESS] Trained autoencoder saved to '{model_filename}'")
    
    # ---------------------------------------------------------
    # 5. CALCULATE RECONSTRUCTION ERROR THRESHOLD ON VAL DATA
    # Threshold = mean(val_reconstruction_error) + 2 * std(val_reconstruction_error)
    # ---------------------------------------------------------
    val_predictions = model.predict(X_val)
    val_mse = np.mean(np.square(X_val - val_predictions), axis=1)
    
    mean_val_mse = np.mean(val_mse)
    std_val_mse = np.std(val_mse)
    threshold = mean_val_mse + (2 * std_val_mse)
    
    threshold_data = {
        'threshold': float(threshold),
        'mean_val_mse': float(mean_val_mse),
        'std_val_mse': float(std_val_mse)
    }
    joblib.dump(threshold_data, os.path.join('processed_data', 'threshold_data.pkl'))
    
    print("\n" + "="*50)
    print("THRESHOLD CALCULATION (Validation Normal Data)")
    print("="*50)
    print(f"Mean Validation MSE : {mean_val_mse:.6f}")
    print(f"Std Validation MSE  : {std_val_mse:.6f}")
    print(f"Calculated Threshold: {threshold:.6f} (Mean + 2 * Std)")
    print("="*50 + "\n")
    
    # ---------------------------------------------------------
    # 6. PLOT AND SAVE TRAINING LOSS CURVE
    # ---------------------------------------------------------
    plt.figure(figsize=(8, 5))
    if 'loss' in history and len(history['loss']) > 0:
        plt.plot(history['loss'], label='Training Loss (MSE)', color='#2b5c8f', linewidth=2)
    if 'val_loss' in history and len(history['val_loss']) > 0:
        plt.plot(history['val_loss'], label='Validation Loss (MSE)', color='#d9534f', linewidth=2, linestyle='--')
        
    plt.title('Autoencoder Training & Validation Loss Curve', fontsize=14, fontweight='bold')
    plt.xlabel('Epochs / Iterations', fontsize=12)
    plt.ylabel('Loss (Mean Squared Error)', fontsize=12)
    plt.legend(fontsize=11)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    
    loss_curve_path = 'loss_curve.png'
    plt.savefig(loss_curve_path, dpi=300)
    plt.close()
    print(f"[SUCCESS] Saved loss curve plot to '{loss_curve_path}'\n")

if __name__ == "__main__":
    train_model(epochs=50, batch_size=32)
