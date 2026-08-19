import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from ml.preprocess import preprocess_data
from models import db, TrainingHistory

def train_and_evaluate(df, save_path, app_context=None):
    X, y, encoders = preprocess_data(df, save_path)
    
    if y is None or len(y) == 0:
        raise ValueError("Target variable 'churn' not found or dataset is empty.")
        
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Define models
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000),
        'Decision Tree': DecisionTreeClassifier(random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42)
    }
    
    best_model = None
    best_acc = 0
    best_name = ""
    results = {}
    
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        results[name] = acc
        if acc > best_acc:
            best_acc = acc
            best_model = model
            best_name = name
            
    # As requested, force Random Forest if it is the best, or default to Random Forest if we just want it
    # We will just take the best model (which often is RF on this dataset)
    
    y_pred_best = best_model.predict(X_test)
    
    metrics = {
        'best_model': best_name,
        'accuracy': accuracy_score(y_test, y_pred_best),
        'precision': precision_score(y_test, y_pred_best),
        'recall': recall_score(y_test, y_pred_best),
        'f1_score': f1_score(y_test, y_pred_best),
        'confusion_matrix': confusion_matrix(y_test, y_pred_best).tolist(),
        'classification_report': classification_report(y_test, y_pred_best, output_dict=True)
    }
    
    # Feature importance for Random Forest
    if hasattr(best_model, 'feature_importances_'):
        importance = best_model.feature_importances_
        feat_imp = pd.DataFrame({'Feature': X.columns, 'Importance': importance})
        feat_imp = feat_imp.sort_values(by='Importance', ascending=False).head(10)
        metrics['feature_importance'] = feat_imp.to_dict(orient='records')
    else:
        metrics['feature_importance'] = []

    # Save model
    joblib.dump(best_model, os.path.join(save_path, 'saved_model.pkl'))
    
    # Save training history to DB if context is provided
    if app_context:
        with app_context:
            history = TrainingHistory(
                accuracy=metrics['accuracy'],
                precision=metrics['precision'],
                recall=metrics['recall'],
                f1_score=metrics['f1_score']
            )
            db.session.add(history)
            db.session.commit()
            
    return metrics
