"""
=============================================================================
STEP 5: EVALUATION AND METRICS (evaluate.py)
=============================================================================
- Evaluates autoencoder performance against true test labels
- Calculates & prints:
    * Accuracy
    * Precision
    * Recall
    * F1-Score
    * Confusion Matrix
- Generates & saves three presentation-ready PNG visualizations:
    1. reconstruction_error_dist.png (Normal vs Anomaly MSE Distribution + Threshold)
    2. confusion_matrix.png (Heatmap visualization)
    3. roc_curve.png (ROC Curve + AUC Score)
=============================================================================
"""

import os
import joblib
import numpy as np

import matplotlib
matplotlib.use('Agg') # Use non-GUI backend for saving plots
import matplotlib.pyplot as plt

import seaborn as sns
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_curve, auc

def evaluate_performance():
    # ---------------------------------------------------------
    # 1. LOAD TEST DATA AND PREDICTIONS
    # ---------------------------------------------------------
    y_test_path = os.path.join('processed_data', 'y_test.npy')
    y_pred_path = os.path.join('processed_data', 'y_pred.npy')
    mse_path = os.path.join('processed_data', 'mse_errors.npy')
    threshold_path = os.path.join('processed_data', 'threshold_data.pkl')
    
    if not os.path.exists(y_test_path) or not os.path.exists(y_pred_path):
        raise FileNotFoundError("Prediction files missing! Run 'python detect_anomalies.py' first.")
        
    y_true = np.load(y_test_path)
    y_pred = np.load(y_pred_path)
    mse_errors = np.load(mse_path)
    threshold_info = joblib.load(threshold_path)
    threshold = threshold_info['threshold']
    
    # ---------------------------------------------------------
    # 2. CALCULATE METRICS
    # ---------------------------------------------------------
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    cm = confusion_matrix(y_true, y_pred)
    
    print("\n" + "="*50)
    print("MODEL EVALUATION PERFORMANCE METRICS")
    print("="*50)
    print(f"Accuracy  : {acc * 100:.2f}%")
    print(f"Precision : {prec * 100:.2f}%")
    print(f"Recall    : {rec * 100:.2f}%")
    print(f"F1-Score  : {f1 * 100:.2f}%")
    print("\nConfusion Matrix:")
    print(f"  TN: {cm[0,0]} | FP: {cm[0,1]}")
    print(f"  FN: {cm[1,0]} | TP: {cm[1,1]}")
    print("="*50 + "\n")
    
    # ---------------------------------------------------------
    # 3. PLOT 1: RECONSTRUCTION ERROR DISTRIBUTION
    # ---------------------------------------------------------
    plt.figure(figsize=(9, 5))
    normal_mse = mse_errors[y_true == 0]
    anomaly_mse = mse_errors[y_true == 1]
    
    plt.hist(normal_mse, bins=50, alpha=0.6, color='#2b5c8f', label='Normal Data MSE')
    plt.hist(anomaly_mse, bins=50, alpha=0.6, color='#d9534f', label='Anomaly Data MSE')
    plt.axvline(threshold, color='black', linestyle='--', linewidth=2, label=f'Threshold ({threshold:.4f})')
    
    plt.title('Reconstruction Error (MSE) Distribution', fontsize=14, fontweight='bold')
    plt.xlabel('Reconstruction Error (MSE)', fontsize=12)
    plt.ylabel('Frequency / Count', fontsize=12)
    plt.legend(fontsize=11)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    
    dist_plot_path = 'reconstruction_error_dist.png'
    plt.savefig(dist_plot_path, dpi=300)
    plt.close()
    print(f"[SUCCESS] Saved Reconstruction Error plot to '{dist_plot_path}'")
    
    # ---------------------------------------------------------
    # 4. PLOT 2: CONFUSION MATRIX HEATMAP
    # ---------------------------------------------------------
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
                xticklabels=['Normal', 'Anomaly'],
                yticklabels=['Normal', 'Anomaly'],
                annot_kws={"size": 14, "weight": "bold"})
    plt.title('Confusion Matrix Heatmap', fontsize=14, fontweight='bold')
    plt.xlabel('Predicted Label', fontsize=12)
    plt.ylabel('True Label', fontsize=12)
    plt.tight_layout()
    
    cm_plot_path = 'confusion_matrix.png'
    plt.savefig(cm_plot_path, dpi=300)
    plt.close()
    print(f"[SUCCESS] Saved Confusion Matrix plot to '{cm_plot_path}'")
    
    # ---------------------------------------------------------
    # 5. PLOT 3: ROC CURVE & AUC SCORE
    # ---------------------------------------------------------
    fpr, tpr, _ = roc_curve(y_true, mse_errors)
    roc_auc = auc(fpr, tpr)
    
    plt.figure(figsize=(7, 5))
    plt.plot(fpr, tpr, color='#28a745', linewidth=2.5, label=f'Autoencoder ROC (AUC = {roc_auc:.4f})')
    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
    plt.title('Receiver Operating Characteristic (ROC) Curve', fontsize=14, fontweight='bold')
    plt.xlabel('False Positive Rate (FPR)', fontsize=12)
    plt.ylabel('True Positive Rate (TPR)', fontsize=12)
    plt.legend(loc='lower right', fontsize=11)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    
    roc_plot_path = 'roc_curve.png'
    plt.savefig(roc_plot_path, dpi=300)
    plt.close()
    print(f"[SUCCESS] Saved ROC Curve plot to '{roc_plot_path}'\n")

if __name__ == "__main__":
    evaluate_performance()
