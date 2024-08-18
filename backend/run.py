import os
import logging
from logging.handlers import StreamHandler
from app import create_app
from app.config import Config

# Create and configure the app
app = create_app(Config)

# Configure logging
if not app.debug:
    stream_handler = StreamHandler()
    stream_handler.setLevel(logging.INFO)
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('WebDoc Parser startup')

# Note: The route definitions for serving the React app have been moved to __init__.py
# This file should not contain any route definitions to avoid conflicts

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=Config.DEBUG)