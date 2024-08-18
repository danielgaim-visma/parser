import os
import logging
from logging.handlers import RotatingFileHandler
from app import create_app
from config import Config

# Create and configure the app
app = create_app()

# Ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

# Configure logging
if not app.debug:
    # Set up the log file handler
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/webdoc_parser.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    # Set the app logger level
    app.logger.setLevel(logging.INFO)
    app.logger.info('WebDoc Parser startup')

# Import and register blueprints
from app.routes.upload_routes import upload as upload_bp
app.register_blueprint(upload_bp)

from app.routes.download_routes import download as download_bp
app.register_blueprint(download_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=Config.DEBUG)