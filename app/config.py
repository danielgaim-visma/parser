import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    RESULTS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
    ALLOWED_EXTENSIONS = {'docx', 'csv', 'txt'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB