from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import os
import logging
from .config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config_class=Config):
    static_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'build')
    app = Flask(__name__, static_folder=static_folder, static_url_path='')
    logger.info(f"Static folder path: {static_folder}")

    CORS(app)
    app.config.from_object(config_class)

    # Ensure the upload and results folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

    # Import and register blueprints
    from .routes.upload_routes import upload
    from .routes.download_routes import download

    app.register_blueprint(upload)
    app.register_blueprint(download)

    @app.route('/api/process', methods=['POST'])
    def process_files():
        # Here you would implement your file processing logic
        # For demonstration, we'll just return some dummy data
        processed_files = ['folder1.zip', 'folder2.zip', 'folder3.zip']
        processed_folders = [
            {'name': f'Folder{i + 1}', 'zipUrl': f'/api/download/{file}'}
            for i, file in enumerate(processed_files)
        ]

        return jsonify({
            'batchId': 'BATCH123',
            'message': 'Processing completed successfully.',
            'processedFolders': processed_folders
        })

    @app.route('/api/download/<filename>')
    def download_file(filename):
        # Ensure the filename is safe
        filename = os.path.basename(filename)

        # Define the directory where your processed files are stored
        processed_dir = app.config['RESULTS_FOLDER']

        # Create the full path to the file
        file_path = os.path.join(processed_dir, filename)

        # Check if the file exists
        if os.path.isfile(file_path):
            return send_from_directory(processed_dir, filename, as_attachment=True)
        else:
            return "File not found", 404

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        logger.info(f"Requested path: {path}")
        if path.startswith('api/'):
            logger.info("API route detected")
            return "Not Found", 404  # Let the API handle its routes

        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            logger.info(f"Serving file: {path}")
            return send_from_directory(app.static_folder, path)

        logger.info("Serving index.html")
        return send_from_directory(app.static_folder, 'index.html')

    @app.errorhandler(404)
    def not_found(e):
        logger.error(f"404 error: {str(e)}")
        return "404 Not Found", 404

    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"500 error: {str(e)}", exc_info=True)
        return "500 Internal Server Error", 500

    @app.before_request
    def log_request_info():
        logger.info(f"Request: {request.method} {request.url}")
        logger.debug(f"Headers: {request.headers}")
        logger.debug(f"Body: {request.get_data()}")

    return app