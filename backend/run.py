import os
import logging
from app import create_app
from app.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = create_app(Config)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    logger.info(f"Starting application on port {port}")
    app.run(host='0.0.0.0', port=port, debug=Config.DEBUG)