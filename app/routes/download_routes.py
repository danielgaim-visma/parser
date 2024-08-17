from flask import Blueprint, send_file, jsonify
import os
from flask import current_app
from ..modules import file_handler

download = Blueprint('download', __name__)
@download.route('/download/<batch_id>')
def download_zip(batch_id):
    try:
        batch_folder = os.path.join(current_app.config['RESULTS_FOLDER'], batch_id)
        if not os.path.exists(batch_folder):
            return jsonify({'error': 'Batch not found'}), 404

        memory_file = file_handler.create_zip_file(batch_folder)
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'batch_{batch_id}.zip'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
