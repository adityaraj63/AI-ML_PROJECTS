# AI Ticket Auto Assignment System

This project is an **IT Helpdesk Ticket Management System** that uses Artificial Intelligence (AI) to automatically route support tickets to the correct department.

## 🚀 What it does
When an employee creates a support ticket (e.g., "My laptop won't turn on"), they don't have to guess which department it goes to. The AI reads the ticket and automatically sends it to the right team (like Hardware, Software, Network, etc.) with over 95% accuracy!

## ✨ Key Features
- **Smart AI Routing**: Automatically predicts the right department for the ticket using Machine Learning.
- **Three Different User Roles**: 
  - **Employee**: Can submit and view their own tickets.
  - **Support Agent**: Can manage and resolve tickets assigned to their department.
  - **Administrator**: Has access to a powerful dashboard with real-time analytics and charts.
- **Dashboard & Analytics**: Shows charts, agent performance, and department workload.
- **Secure System**: Includes login authentication and data protection.

## 💻 Tech Stack
- **Backend:** Python and Flask
- **AI / Machine Learning:** scikit-learn (TF-IDF model)
- **Database:** SQLite / MySQL
- **Frontend:** HTML, CSS (Bootstrap 5), JavaScript

## 🏃 How to Run the Project Locally
1. Install Python on your computer.
2. Clone this repository and open the folder.
3. Install the required packages: `pip install -r requirements.txt`
4. Set up the database: `flask init-db`
5. Generate data and train the AI model: `flask train-model`
6. Run the app: `flask run` (or `python run.py`)
7. Open `http://localhost:5000` in your web browser.

## 🔑 Default Login Credentials
- **Admin:** `admin@company.com` | Password: `Admin@123456`
- **Agent:** `alice@company.com` | Password: `Password@123`
- **Employee:** `emma@company.com` | Password: `Password@123`

*(For more technical details and Docker instructions, see `README_Advanced.md`)*
