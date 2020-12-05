
class Config:
    SECRET_KEY = "dev secret key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///radiologyassistant.db"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024