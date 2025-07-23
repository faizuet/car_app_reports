from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # ✅ Set the password using hashing
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # ✅ Check password during login
    def check_password(self, password):
        return check_password_hash(self.password, password)
