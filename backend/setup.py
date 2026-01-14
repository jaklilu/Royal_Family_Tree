"""
Helper script to initialize the database and create initial migration.
Run this after setting up your virtual environment and .env file.
"""
import os
import sys
from flask import Flask
from flask_migrate import init, migrate, upgrade
from app import create_app, db

def setup_database():
    """Initialize database and run migrations"""
    app = create_app()
    
    with app.app_context():
        # Check if migrations directory exists
        migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
        
        if not os.path.exists(migrations_dir):
            print("Initializing migrations...")
            init()
        
        print("Creating migration...")
        migrate(message="Initial migration")
        
        print("Applying migration...")
        upgrade()
        
        print("Database setup complete!")

if __name__ == '__main__':
    if not os.environ.get('DATABASE_URL'):
        print("ERROR: DATABASE_URL environment variable not set!")
        print("Please create a .env file with your database configuration.")
        sys.exit(1)
    
    setup_database()

