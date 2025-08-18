from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    _password_hash = db.Column("password", db.String(128), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    @property
    def password(self):
        raise AttributeError("Password is write-only.")

    @password.setter
    def password(self, plaintext_password):
        """Allows setting password via: user.password = 'mypassword'"""
        self._password_hash = generate_password_hash(plaintext_password)

    def set_password(self, plaintext_password):
        """Explicit method for compatibility with your auth route"""
        self._password_hash = generate_password_hash(plaintext_password)

    def check_password(self, password):
        """Verify a password against the stored hash"""
        return check_password_hash(self._password_hash, password)

