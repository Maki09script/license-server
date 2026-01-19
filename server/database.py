import os
import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()

class LicenseKey(db.Model):
    __tablename__ = 'license_keys'

    id = db.Column(db.Integer, primary_key=True)
    key_code = db.Column(db.String(64), unique=True, nullable=False)
    
    # Type: 'timed' or 'lifetime'
    key_type = db.Column(db.String(20), nullable=False, default='timed')
    
    # Duration in seconds for timed keys (stored for reference)
    duration_seconds = db.Column(db.Integer, nullable=True)
    
    # HWID Binding
    hwid = db.Column(db.String(128), nullable=True)
    
    # Status
    is_banned = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    activated_at = db.Column(db.DateTime(timezone=True), nullable=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=True)

    def to_dict(self):
        return {
            "key": self.key_code,
            "type": self.key_type,
            "hwid": self.hwid,
            "is_banned": self.is_banned,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_valid": self.is_valid()
        }

    def is_valid(self):
        if self.is_banned:
            return False
        if self.key_type == 'lifetime':
            return True
        if self.expires_at:
            # Check if expired
            # SQLite might return naive datetimes, so enforce UTC if needed
            exp = self.expires_at
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=datetime.timezone.utc)
            
            return datetime.datetime.now(datetime.timezone.utc) < exp
        # Not activated yet, so valid
        return True

def init_db(app):
    # Check for DATABASE_URL environment variable (Render.com provides this)
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # Fix for SQLAlchemy: Render uses 'postgres://', but SQLAlchemy needs 'postgresql://'
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Fallback to local SQLite for testing
        db_path = os.path.join(os.path.dirname(__file__), 'licenses.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
