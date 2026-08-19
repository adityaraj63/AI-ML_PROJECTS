from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash

def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()
        # Check if admin exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully. (username: admin, password: admin123)")
        else:
            print("Admin user already exists.")

if __name__ == '__main__':
    init_db()
