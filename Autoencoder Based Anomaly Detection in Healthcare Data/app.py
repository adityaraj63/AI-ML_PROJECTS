"""
=============================================================================
STEP 6: STREAMLIT DASHBOARD (app.py)
=============================================================================
A clean, minimal, non-complex web dashboard built with Streamlit.

Features:
1. Upload patient CSV dataset (e.g. sample_patient_upload.csv)
2. Run trained Autoencoder anomaly detection model
3. Display detailed results table with "Normal" / "Anomaly" labels & MSE scores
4. Display summary bar chart (Normal vs Anomaly counts)
5. Downloadable results CSV
=============================================================================
"""

import os
import joblib
import numpy as np
import pandas as pd
import streamlit as st
from model import load_saved_model

# Set Streamlit page config
st.set_page_config(
    page_title="Healthcare Anomaly Detection",
    page_icon="🏥",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background-color: #2563EB;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        border: none;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🏥 Autoencoder Healthcare Anomaly Detection</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">B.Tech Project: Detect abnormal patient vitals using Deep Autoencoders</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# LOAD TRAINED ASSETS
# ---------------------------------------------------------
@st.cache_resource
def load_assets():
    model_path = 'autoencoder_model.h5'
    scaler_path = os.path.join('processed_data', 'scaler.pkl')
    threshold_path = os.path.join('processed_data', 'threshold_data.pkl')
    feature_cols_path = os.path.join('processed_data', 'feature_cols.pkl')

    if not all([os.path.exists(p) for p in [scaler_path, threshold_path, feature_cols_path]]):
        return None, None, None, None

    try:
        model = load_saved_model(model_path)
    except Exception:
        return None, None, None, None

    scaler = joblib.load(scaler_path)
    threshold_info = joblib.load(threshold_path)
    threshold = threshold_info['threshold']
    feature_cols = joblib.load(feature_cols_path)

    return model, scaler, threshold, feature_cols

model, scaler, threshold, feature_cols = load_assets()

if model is None:
    st.error("⚠️ Model or preprocessed artifacts not found! Please run `python run_all.py` first to train the model.")
    st.stop()

# Sidebar Info
st.sidebar.header("📌 Model Status & Specs")
st.sidebar.success("Autoencoder Model Loaded")
st.sidebar.info(f"**Anomaly Threshold (MSE):** `{threshold:.5f}`")
st.sidebar.write(f"**Required Features ({len(feature_cols)}):**")
for col in feature_cols:
    st.sidebar.markdown(f"- `{col}`")

# ---------------------------------------------------------
# FILE UPLOAD & PREDICTION SECTION
# ---------------------------------------------------------
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Upload Patient Data (CSV)")
    uploaded_file = st.file_uploader("Upload CSV file containing patient vitals", type=["csv"])
    
    # Direct sample loader option
    sample_file_path = os.path.join('data', 'sample_patient_upload.csv')
    if os.path.exists(sample_file_path):
        if st.button("📁 Load Default Sample Patient Data"):
            uploaded_file = sample_file_path

with col2:
    st.subheader("2. Quick Instructions")
    st.markdown("""
    - Ensure your CSV file contains columns corresponding to patient features.
    - Click **Run Anomaly Detection** below to process data through the Autoencoder.
    - Samples with **Reconstruction Error (MSE) > Threshold** are flagged as **Anomaly**.
    """)

if uploaded_file is not None:
    try:
        if isinstance(uploaded_file, str):
            input_df = pd.read_csv(uploaded_file)
        else:
            input_df = pd.read_csv(uploaded_file)
            
        st.markdown("---")
        st.subheader("📋 Input Data Preview")
        st.dataframe(input_df.head(10), use_container_width=True)
        
        # Check if target column exists (optional) and separate features
        target_col = 'target'
        if target_col in input_df.columns:
            features_df = input_df.drop(columns=[target_col])
        else:
            features_df = input_df.copy()
            
        # Match columns with trained feature columns
        missing_cols = [c for c in feature_cols if c not in features_df.columns]
        if missing_cols:
            st.error(f"❌ Missing required columns in uploaded CSV: `{missing_cols}`")
            st.stop()
            
        features_df = features_df[feature_cols]
        
        if st.button("🚀 Run Anomaly Detection Model"):
            with st.spinner("Processing records through Autoencoder..."):
                # Scale input data
                X_scaled = scaler.transform(features_df.values)
                
                # Predict reconstructions
                reconstructions = model.predict(X_scaled)
                
                # Calculate MSE per row
                mse_scores = np.mean(np.square(X_scaled - reconstructions), axis=1)
                
                # Classify
                predictions = (mse_scores > threshold).astype(int)
                labels = ["🚨 Anomaly" if p == 1 else "✅ Normal" for p in predictions]
                
                # Build Result Dataframe
                result_df = input_df.copy()
                result_df['Reconstruction_Error_MSE'] = np.round(mse_scores, 5)
                result_df['Status'] = labels
                
                normal_count = sum(predictions == 0)
                anomaly_count = sum(predictions == 1)
                
                # Display Metrics
                st.markdown("---")
                st.subheader("📊 Detection Results Summary")
                
                mcol1, mcol2, mcol3, mcol4 = st.columns(4)
                mcol1.metric("Total Patients Processed", len(result_df))
                mcol2.metric("Normal Patients", normal_count)
                mcol3.metric("Anomalies Detected", anomaly_count, delta=f"{anomaly_count/len(result_df)*100:.1f}% Anomalies", delta_color="inverse")
                mcol4.metric("Applied MSE Threshold", f"{threshold:.5f}")
                
                # Visualization: Bar Chart
                chart_data = pd.DataFrame({
                    'Category': ['Normal', 'Anomaly'],
                    'Count': [normal_count, anomaly_count]
                })
                
                ccol1, ccol2 = st.columns([1, 1])
                
                with ccol1:
                    st.write("**Patient Status Distribution**")
                    st.bar_chart(chart_data.set_index('Category'))
                    
                with ccol2:
                    st.write("**Detailed Patient Status Table**")
                    st.dataframe(result_df, use_container_width=True)
                    
                    # Download CSV button
                    csv_data = result_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Anomaly Report (CSV)",
                        data=csv_data,
                        file_name="healthcare_anomaly_detection_report.csv",
                        mime="text/csv"
                    )

    except Exception as e:
        st.error(f"Error processing CSV file: {str(e)}")

st.markdown("---")
st.caption("Autoencoder Anomaly Detection Healthcare System | Developed for B.Tech Final Year Presentation")
