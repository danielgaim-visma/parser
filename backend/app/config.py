import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    RESULTS_FOLDER = os.path.join(BASE_DIR, 'results')
    ALLOWED_EXTENSIONS = {'docx', 'csv', 'txt'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    CORS_HEADERS = 'Content-Type'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False') == 'True'