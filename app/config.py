class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///car_database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'super-secret-key'  # change this to something strong in production
