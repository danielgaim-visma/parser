# app.py

from flask import Flask, render_template, request, jsonify, send_file
import os
import logging
from werkzeug.utils import secure_filename
from docx_parser_functions import parse_docx, create_word_count_summary
import uuid
import zipfile
import io

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
ALLOWED_EXTENSIONS = {'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size

# Set up logging
logging.basicConfig(level=logging.DEBUG)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_zip_file(batch_folder):
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(batch_folder):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, batch_folder)
                zf.write(file_path, arcname)
    memory_file.seek(0)
    return memory_file


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    app.logger.info("Upload request received")
    if 'files[]' not in request.files:
        app.logger.error("No file part in the request")
        return jsonify({'error': 'No file part'})

    files = request.files.getlist('files[]')
    if not files or files[0].filename == '':
        app.logger.error("No selected files")
        return jsonify({'error': 'No selected files'})

    batch_id = str(uuid.uuid4())
    batch_folder = os.path.join(app.config['RESULTS_FOLDER'], batch_id)
    os.makedirs(batch_folder, exist_ok=True)
    app.logger.info(f"Created batch folder: {batch_folder}")

    parse_doc = request.form.get('parse_doc') == 'true'
    create_summary = request.form.get('create_summary') == 'true'
    min_count = int(request.form.get('min_count', 5))
    max_count = int(request.form.get('max_count', 80))

    app.logger.info(
        f"parse_doc: {parse_doc}, create_summary: {create_summary}, min_count: {min_count}, max_count: {max_count}")

    results = []
    filenames = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(upload_path)
            filenames.append(filename)

            app.logger.info(f"File saved: {upload_path}")

            result = {'filename': filename}
            if parse_doc:
                app.logger.info(f"Parsing document: {filename}")
                doc_folder = parse_docx(upload_path, batch_folder)
                result['doc_folder'] = os.path.relpath(doc_folder, batch_folder)
                app.logger.info(f"Document parsed and saved in: {doc_folder}")

            results.append(result)

    if create_summary:
        app.logger.info("Creating word count summary")
        summary_file = create_word_count_summary(filenames, batch_folder, min_count, max_count)
        if summary_file:
            summary_filename = os.path.basename(summary_file)
            results.append({'summary_file': summary_filename})
            app.logger.info(f"Summary file saved: {summary_file}")
        else:
            app.logger.warning("No word count summary created (no words matched the criteria)")

    app.logger.info(f"Processing complete. Results: {results}")
    return jsonify({'results': results, 'batch_id': batch_id})


@app.route('/download/<batch_id>')
def download_zip(batch_id):
    batch_folder = os.path.join(app.config['RESULTS_FOLDER'], batch_id)
    if not os.path.exists(batch_folder):
        return jsonify({'error': 'Batch not found'}), 404

    memory_file = create_zip_file(batch_folder)
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'batch_{batch_id}.zip'
    )


@app.route('/clear', methods=['POST'])
def clear():
    try:
        # Clear upload folder
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        app.logger.info("Upload folder cleared")
        return jsonify({'message': 'Cleared successfully'})
    except Exception as e:
        app.logger.error(f"Error clearing upload folder: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(RESULTS_FOLDER, exist_ok=True)
    app.run(debug=True)