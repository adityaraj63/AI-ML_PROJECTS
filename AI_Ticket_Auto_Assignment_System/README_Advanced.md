# AI Ticket Auto Assignment System 🤖

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-3.0-green?logo=flask" />
  <img src="https://img.shields.io/badge/scikit--learn-1.5-orange?logo=scikit-learn" />
  <img src="https://img.shields.io/badge/MySQL-8.0-blue?logo=mysql" />
  <img src="https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap" />
  <img src="https://img.shields.io/badge/Docker-Ready-blue?logo=docker" />
</p>

> An enterprise-grade AI-powered IT Helpdesk Ticket Management System that **automatically classifies** incoming support tickets to the correct department using NLP and Machine Learning.

---

## 🌟 Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI Auto-Classification** | Predicts department with confidence score using TF-IDF + ML |
| 🎯 **95%+ Accuracy** | Trained on 10,000 synthetic tickets across 10 departments |
| 👥 **3 User Roles** | Employee, Support Agent, Administrator |
| 📊 **Real-time Analytics** | Charts, KPIs, department workload, agent performance |
| 🔒 **Enterprise Security** | RBAC, CSRF, password hashing, audit logs |
| 🐳 **Docker Ready** | Full docker-compose with MySQL |
| 🌐 **REST API** | Complete JSON API for all features |
| 🎨 **Premium Dark UI** | Glassmorphism design with animations |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Flask Application                   │
├──────────┬──────────┬──────────┬──────────┬─────────┤
│  Auth    │Employee  │  Admin   │  Agent   │  API    │
│Blueprint │Blueprint │Blueprint │Blueprint │Blueprint│
├──────────┴──────────┴──────────┴──────────┴─────────┤
│                  Services Layer                      │
│   ticket_service  │  analytics_service               │
├─────────────────────────────────────────────────────┤
│               ML Pipeline                           │
│  Preprocessor → TF-IDF → [LR | NB | SVM] → Best   │
├─────────────────────────────────────────────────────┤
│              SQLAlchemy ORM + MySQL                 │
│  Users │ Tickets │ Departments │ PredictionLogs    │
└─────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
AI Ticket Auto Assignment System/
├── app/
│   ├── __init__.py          # App factory
│   ├── config.py            # Configuration classes
│   ├── extensions.py        # Flask extensions
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   ├── ticket.py
│   │   ├── department.py
│   │   └── prediction_log.py
│   ├── routes/              # Flask blueprints
│   │   ├── auth.py          # Login, register, logout
│   │   ├── employee.py      # Employee portal
│   │   ├── admin.py         # Admin dashboard
│   │   ├── agent.py         # Support agent portal
│   │   └── api.py           # REST API
│   ├── services/            # Business logic
│   │   ├── ticket_service.py
│   │   └── analytics_service.py
│   ├── ml/                  # Machine Learning
│   │   ├── dataset_generator.py  # 10K ticket generator
│   │   ├── preprocessor.py       # NLP pipeline
│   │   ├── trainer.py            # Model training
│   │   ├── predictor.py          # Prediction service
│   │   └── saved_models/         # Trained models
│   ├── templates/           # Jinja2 HTML templates
│   ├── static/              # CSS, JS, images
│   └── utils/               # Helpers & decorators
├── dataset/                 # Generated CSV dataset
├── tests/                   # Unit tests
├── docs/                    # Documentation
├── run.py                   # Entry point
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- MySQL 8.0+ (or use Docker)
- Git

### Option 1: Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-org/ai-ticket-system.git
cd "AI Ticket Auto Assignment System"

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate       # Linux/Mac
.\venv\Scripts\Activate.ps1    # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your MySQL credentials

# 5. Create MySQL database
mysql -u root -p -e "CREATE DATABASE ai_ticket_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 6. Initialize database (creates tables + seeds data)
flask init-db

# 7. Generate dataset & train AI model
flask train-model

# 8. Run the application
flask run
```

### Option 2: Docker (Recommended)

```bash
# 1. Clone and configure
cp .env.example .env   # Edit if needed

# 2. Build and start everything
docker-compose up --build -d

# 3. Initialize database (first time)
docker exec ai_ticket_app flask init-db

# 4. Train the model
docker exec ai_ticket_app flask train-model

# 5. Open browser: http://localhost:5000
```

---

## 🔑 Default Login Credentials

| Role | Email | Password |
|------|-------|----------|
| **Administrator** | admin@company.com | Admin@123456 |
| **Support Agent** | alice@company.com | Password@123 |
| **Employee** | emma@company.com | Password@123 |

---

## 🤖 Machine Learning Pipeline

### Data Generation
- **10,000 synthetic tickets** across 10 IT departments
- Template-based generation with randomized variables
- Realistic IT support language patterns

### NLP Preprocessing
1. Lowercase conversion
2. URL and email removal
3. Punctuation stripping
4. Tokenization (NLTK)
5. Stopword removal (English + domain-specific)
6. Lemmatization (WordNet)

### Models Trained
| Model | Typical Accuracy | F1 Score |
|-------|-----------------|----------|
| Logistic Regression | 96-98% | 0.96-0.98 |
| Multinomial Naive Bayes | 92-95% | 0.92-0.95 |
| Linear SVM | 95-97% | 0.95-0.97 |

The **best model is auto-selected** based on weighted F1 score.

### TF-IDF Configuration
```python
TfidfVectorizer(
    max_features=15000,
    ngram_range=(1, 2),    # unigrams + bigrams
    sublinear_tf=True,
    min_df=2,
    max_df=0.95
)
```

---

## 🌐 REST API Reference

### Authentication
All API endpoints require authentication (Flask session).

### Prediction API
```
POST /api/v1/predict
Content-Type: application/json

{
  "title": "My laptop won't turn on",
  "description": "The laptop battery is dead and the charger is broken"
}

Response:
{
  "success": true,
  "data": {
    "predicted_department": "Hardware",
    "confidence": 96.4,
    "priority": "high",
    "estimated_resolution_hours": 4.0,
    "keywords": ["laptop", "battery", "charger"],
    "all_probabilities": { "Hardware": 0.964, "Software": 0.018, ... }
  }
}
```

### Tickets API
```
GET    /api/v1/tickets               # List tickets (paginated)
POST   /api/v1/tickets               # Create ticket with AI
GET    /api/v1/tickets/{id}          # Get ticket
PATCH  /api/v1/tickets/{id}/status   # Update status
```

### Other Endpoints
```
GET /api/v1/auth/me                  # Current user info
GET /api/v1/departments              # List departments
GET /api/v1/analytics/dashboard      # Dashboard stats (admin)
GET /api/v1/analytics/charts         # Chart data (admin)
GET /api/v1/ml/status                # ML model status
```

---

## 🏢 Supported Departments

| Department | SLA | Description |
|-----------|-----|-------------|
| Hardware | 8h | Physical devices, peripherals |
| Software | 4h | Application issues, installations |
| Network | 2h | Internet, VPN, WiFi |
| Database | 6h | DB errors, performance |
| Cloud | 4h | AWS/Azure/GCP infrastructure |
| Security | 1h | Breaches, phishing, access |
| HR | 24h | HR portal, payroll, leaves |
| Finance | 48h | Invoices, ERP, expenses |
| CRM Support | 12h | Salesforce, customer data |
| DevOps | 3h | CI/CD, deployments |

---

## 🔒 Security Features

- **Password Hashing**: Werkzeug PBKDF2-SHA256
- **CSRF Protection**: Flask-WTF on all forms
- **Role-Based Access Control**: Employee / Agent / Admin
- **Input Sanitization**: Bleach HTML sanitization
- **SQL Injection Prevention**: SQLAlchemy ORM
- **Audit Logging**: All actions logged with IP address
- **Session Security**: HTTPOnly, SameSite cookies

---

## 🐳 Environment Variables

```env
SECRET_KEY=your-secret-key-32-chars-minimum
DB_HOST=localhost
DB_PORT=3306
DB_NAME=ai_ticket_db
DB_USER=root
DB_PASSWORD=your_password
ADMIN_EMAIL=admin@company.com
ADMIN_PASSWORD=Admin@123456
FLASK_ENV=development
```

---

## 🧪 Running Tests

```bash
# Install test dependencies
pip install pytest pytest-flask

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

---

## 📊 Database ER Diagram

```
users ──────────── tickets ────────── departments
  │                  │                    │
  │              prediction_logs          │
  │                  │                    │
  └────────── activity_logs ─────────────┘
```

---

## 🚀 Deployment on Render

1. Connect your GitHub repository
2. Set **Build Command**: `pip install -r requirements.txt`
3. Set **Start Command**: `gunicorn run:app`
4. Add environment variables in Render dashboard
5. Add MySQL add-on (JawsDB or PlanetScale)

---

## 🛣️ Future Enhancements

- [ ] Email notifications on ticket events
- [ ] Natural Language feedback learning (active learning)
- [ ] Ticket similarity using sentence embeddings
- [ ] Slack / Teams integration
- [ ] Mobile application (React Native)
- [ ] Multi-language support
- [ ] SLA breach auto-escalation
- [ ] Report export (PDF/Excel)

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) file.

---

<p align="center">Built with ❤️ using Flask, scikit-learn, and Bootstrap 5</p>
