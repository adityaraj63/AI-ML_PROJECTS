import os
import joblib
from ml.preprocess import preprocess_input

def get_risk_level(probability):
    if probability >= 0.7:
        return 'High Risk'
    elif probability >= 0.4:
        return 'Medium Risk'
    else:
        return 'Low Risk'

def predict_churn(input_data, models_path):
    """
    input_data: list of dictionaries or DataFrame
    models_path: path where saved_model.pkl and encoders.pkl are stored
    """
    model_file = os.path.join(models_path, 'saved_model.pkl')
    encoders_file = os.path.join(models_path, 'encoders.pkl')
    
    if not os.path.exists(model_file) or not os.path.exists(encoders_file):
        raise FileNotFoundError("Model or encoders not found. Please train the model first.")
        
    model = joblib.load(model_file)
    
    # Preprocess
    X = preprocess_input(input_data, models_path)
    
    # Predict
    predictions = model.predict(X)
    probabilities = model.predict_proba(X)[:, 1] # Probability of Class 1 (Churn)
    
    results = []
    for pred, prob in zip(predictions, probabilities):
        results.append({
            'prediction': 'Yes' if pred == 1 else 'No',
            'probability': float(prob),
            'risk_level': get_risk_level(prob)
        })
        
    return results
