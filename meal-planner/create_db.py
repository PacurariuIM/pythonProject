from main import app, db

with app.app_context():
    db.drop_all()  # This will drop all tables, make sure you don't need existing data
    db.create_all()  # Create all tables
    print("Database tables created successfully!")

