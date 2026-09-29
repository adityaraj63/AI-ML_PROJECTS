# AI Ticket Auto Assignment System

## 1. Project Title
AI Ticket Auto Assignment System

## 2. Project Aim
The system automatically analyzes a customer support ticket, predicts its category using Machine Learning, and automatically assigns the ticket to the appropriate support team.

## 3. Problem Statement
Customer support teams often receive hundreds of tickets daily. Manually reading and categorizing these tickets is time-consuming, prone to human error, and delays the resolution process. This inefficiency impacts customer satisfaction.

## 4. Solution
This project automates the ticket assignment process using Natural Language Processing (NLP) and Machine Learning. By analyzing the text of the ticket, an ML model predicts the ticket category and assigns it to the relevant support team instantly.

## 5. Features
- **Machine Learning Classification**: Automatically categorizes tickets into Technical, Billing, Account, Network, or General.
- **Smart Assignment**: Maps the predicted category to the specific support team.
- **Confidence Scoring**: Displays the AI's confidence percentage for its prediction.
- **Dashboard**: Simple, clean overview of ticket statistics and recent assignments.
- **Ticket History**: View all previously submitted and categorized tickets.
- **Responsive UI**: Clean, professional web interface built with HTML/CSS.

## 6. Technologies Used
- **Python**: Core programming language.
- **Scikit-learn**: Machine learning model training and evaluation.
- **Pandas & NumPy**: Data processing and manipulation.
- **Django**: Web framework for building the application.
- **SQLite**: Database to store tickets.
- **HTML, CSS, Basic JavaScript**: Frontend user interface.

## 7. Machine Learning Workflow
1. **Data Collection**: A dataset of 500 realistic support tickets was created.
2. **Data Cleaning & EDA**: Missing values were checked and category distributions plotted.
3. **Feature Engineering**: Used **TF-IDF (Term Frequency-Inverse Document Frequency)** to convert the text descriptions into numerical data that the ML model can understand.
4. **Model Training**: Trained a **Logistic Regression** classifier on the processed data.
5. **Evaluation**: Evaluated the model using accuracy score, confusion matrix, and classification report.
6. **Model Saving**: Saved the trained model and vectorizer using `joblib` for integration with Django.

## 8. Project Architecture
```
User enters ticket -> Django receives ticket -> Load saved ML model & TF-IDF vectorizer -> Transform ticket text -> Predict category -> Calculate confidence -> Map category to support team -> Save to SQLite -> Display result
```

## 9. Dataset Description
The dataset contains 500 support tickets with two columns:
- `ticket_description`: The text content of the user's issue.
- `category`: The classification of the issue.

The 5 categories are: Technical, Billing, Account, Network, General.

## 10. Model Used
- **TF-IDF Vectorizer**: Used to convert words to numerical features based on term frequency and inverse document frequency.
- **Logistic Regression**: Chosen for its simplicity, efficiency, and excellent performance on text classification tasks.

## 11. How to Install
1. Clone the repository:
   ```bash
   git clone <repo-url>
   ```
2. Navigate to the project directory:
   ```bash
   cd AI-Ticket-Auto-Assignment
   ```
3. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 12. How to Run
1. Generate the dataset and train the model (if not already done):
   ```bash
   python generate_dataset.py
   python train_model.py
   ```
2. Run database migrations:
   ```bash
   python manage.py makemigrations tickets
   python manage.py migrate
   ```
3. Start the Django development server:
   ```bash
   python manage.py runserver
   ```
4. Open your browser and go to `http://127.0.0.1:8000/`.

## 13. Example Predictions
**Input:** "My internet is not working even though my Wi-Fi is connected."
**Output:** 
- Category: Network
- Assigned Team: Network Support
- Confidence: 91%

**Input:** "I was charged twice for my subscription."
**Output:**
- Category: Billing
- Assigned Team: Billing Support
- Confidence: 82%

## 14. Screenshots
*(Add screenshots of Dashboard, Create Ticket, and Ticket History pages here)*

## 15. Future Improvements
- Integrate a real-world, larger dataset from platforms like Kaggle.
- Add user authentication to allow customers to view only their own tickets.
- Expand categories and support teams.
- Deploy the application to a cloud platform like Heroku or PythonAnywhere.
