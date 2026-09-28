# 🏥 Autoencoder Based Anomaly Detection in Healthcare Data

Welcome to this simple and easy-to-understand project for detecting unusual health patterns using Machine Learning! This was built as a complete end-to-end B.Tech final year project.

## 🌟 What does this project do?
Imagine a security guard who only knows what "normal" behavior looks like. If someone starts acting strangely, the guard instantly flags them as suspicious. 

This project works exactly like that! We train a special Machine Learning model called an **Autoencoder** on *only normal* patient health records (like heart rate, blood pressure, temperature, etc.). 

When we give the model a new patient's data:
- If the patient is healthy, the model easily recognizes the pattern.
- If the patient has abnormal vitals, the model gets confused and makes a "high error" when trying to understand it.
- **High Error = Anomaly Detected! 🚨**

## 📂 Project Structure
- `generate_dataset.py`: Creates a fake healthcare dataset for us to practice with.
- `data_preprocessing.py`: Cleans up the data so the model can understand it.
- `model.py`: The brain of our project (The Autoencoder).
- `train.py`: Teaches the model what "normal" health looks like.
- `detect_anomalies.py`: Tests the model to see if it can catch the sick patients.
- `evaluate.py`: Checks how accurate our model is and draws nice graphs.
- `app.py`: A beautiful web dashboard where you can upload patient data and see results instantly!

## 🚀 How to Run the Project

### 1. Install Required Tools
Open your terminal or command prompt and type:
```bash
pip install -r requirements.txt
```

### 2. Run the Full Pipeline
You can run the entire project (creating data, training the model, and testing it) with just one command!
```bash
python run_all.py
```

### 3. Open the Web Dashboard
Want to see it in action? Run this command to open the interactive web app:
```bash
streamlit run app.py
```
This will open a website in your browser where you can upload the `sample_patient_upload.csv` file (found in the `data/` folder) and detect anomalies yourself!

## 📊 Results Generated
After running the project, you will get:
1. **autoencoder_model**: The trained brain saved for future use.
2. **loss_curve.png**: A graph showing how well the model learned.
3. **reconstruction_error_dist.png**: A graph showing the difference between normal and abnormal patients.
4. **confusion_matrix.png**: A report card showing how many predictions were right or wrong.
5. **roc_curve.png**: An accuracy curve plot.

Enjoy exploring the project!
