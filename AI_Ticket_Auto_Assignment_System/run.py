"""
AI Ticket Auto Assignment System
Flask Application Entry Point
"""
import os
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.department import Department
from app.models.ticket import Ticket
from app.models.prediction_log import PredictionLog, ActivityLog

app = create_app()


@app.shell_context_processor
def make_shell_context():
    """Expose models in flask shell for debugging."""
    return {
        "db": db,
        "User": User,
        "Department": Department,
        "Ticket": Ticket,
        "PredictionLog": PredictionLog,
        "ActivityLog": ActivityLog,
    }


@app.cli.command("init-db")
def init_db():
    """Initialize the database and seed default data."""
    from app.utils.seeder import seed_all
    db.create_all()
    seed_all()
    print("[OK] Database initialized and seeded successfully.")


@app.cli.command("train-model")
def train_model():
    """Generate dataset and train the ML model."""
    from app.ml.dataset_generator import generate_and_save_dataset
    from app.ml.trainer import train_and_save_best_model
    print("[INFO] Generating dataset...")
    generate_and_save_dataset()
    print("[INFO] Training models...")
    train_and_save_best_model()
    print("[OK] Model trained and saved successfully.")


@app.cli.command("generate-dataset")
def generate_dataset():
    """Only generate the dataset."""
    from app.ml.dataset_generator import generate_and_save_dataset
    generate_and_save_dataset()
    print("[OK] Dataset generated successfully.")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "development") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
