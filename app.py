import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Desktop mode detection
DESKTOP_MODE = os.environ.get("DESKTOP_MODE", "false").lower() == "true"

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Enforce secret key requirement
if not app.secret_key:
    raise RuntimeError("SESSION_SECRET environment variable is required for secure sessions")

# ProxyFix only needed for web mode
if not DESKTOP_MODE:
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# configure the database
if DESKTOP_MODE:
    # Desktop mode - use paths from environment or defaults
    database_url = os.environ.get("DATABASE_URL", "sqlite:///tracking.db")
    upload_folder = os.environ.get("UPLOADS_FOLDER", "uploads")
    logs_folder = os.environ.get("LOGS_FOLDER", "logs")
else:
    # Web mode - use PostgreSQL and relative paths
    database_url = os.environ.get("DATABASE_URL", "sqlite:///tracking.db")
    upload_folder = "uploads"
    logs_folder = "logs"

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = database_url

# SQLite-specific optimizations for desktop mode
if database_url.startswith('sqlite'):
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "connect_args": {"check_same_thread": False},
    }
    
    # Configure SQLite for better concurrency
    from sqlalchemy import event
    from sqlalchemy.engine import Engine
    
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        if 'sqlite' in str(dbapi_connection):
            cursor = dbapi_connection.cursor()
            # Enable WAL mode for better concurrency
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA synchronous=NORMAL;")
            cursor.execute("PRAGMA cache_size=10000;")
            cursor.execute("PRAGMA temp_store=memory;")
            cursor.close()
else:
    # PostgreSQL configuration
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

# File handling configuration
app.config["UPLOAD_FOLDER"] = upload_folder
app.config["LOGS_FOLDER"] = logs_folder
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100MB max file size
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 31536000

# Create directories if they don't exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["LOGS_FOLDER"], exist_ok=True)

# initialize the app with the extension
db.init_app(app)

with app.app_context():
    try:
        # Import models
        import models
        
        # Create all tables
        db.create_all()
        logging.info("Database tables created successfully")
    except Exception as e:
        logging.error(f"Failed to initialize database: {str(e)}")
        # Don't raise the exception here, let the app start but log the error
        pass

# Register routes after app context
from routes import *
