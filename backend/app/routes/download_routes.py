from flask import Blueprint, send_file, current_app, abort
import os
from werkzeug.utils import secure_filename

download = Blueprint('download', __name__)

@download.route('/api/download/<path:filename>', methods=['GET'])
def download_file(filename):
    # Secure the filename to prevent directory traversal attacks
    filename = secure_filename(filename)

    # Construct the full path to the file
    file_path = os.path.join(current_app.config['RESULTS_FOLDER'], filename)

    # Check if the file exists
    if os.path.exists(file_path) and os.path.isfile(file_path):
        try:
            return send_file(file_path, as_attachment=True)
        except Exception as e:
            current_app.logger.error(f"Error sending file: {e}")
            abort(500)
    else:
        current_app.logger.warning(f"File not found: {file_path}")
        abort(404)


@download.errorhandler(404)
def not_found_error(error):
    return "File not found", 404


@download.errorhandler(500)
def internal_error(error):
    return "Internal server error", 500