import os
import sys
import logging
from app import create_app
from app.config import Config

# Create and configure the app
app = create_app(Config)

# Configure logging
if not app.debug:
    # Set up the stream handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    stream_handler.setLevel(logging.INFO)
    app.logger.addHandler(stream_handler)

    # Set the app logger level
    app.logger.setLevel(logging.INFO)
    app.logger.info('WebDoc Parser startup')

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5001)), debug=Config.DEBUG)