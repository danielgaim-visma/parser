import os
from flask import Flask
from flask_cors import CORS
from app.routes import main, upload, download

def create_app():
    app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
    CORS(app)

    # Configuration
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'uploads')
    app.config['RESULTS_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'results')
    app.config['ALLOWED_EXTENSIONS'] = {'docx', 'csv', 'txt'}
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

    # Ensure upload and results folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

    # Register blueprints
    app.register_blueprint(main)
    app.register_blueprint(upload)
    app.register_blueprint(download)

    @app.route('/')
    def serve():
        return app.send_static_file('index.html')

    @app.errorhandler(404)
    def not_found(e):
        return app.send_static_file('index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, use_reloader=True, port=5001)  # Changed port to 5001
