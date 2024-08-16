from flask import Flask, render_template, request, jsonify, send_file
import os
import logging
from werkzeug.utils import secure_filename
from docx_parser_functions import parse_docx, create_word_count_summary, read_keywords
import uuid
import zipfile
import io

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
ALLOWED_EXTENSIONS = {'docx', 'csv', 'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
    logger.info("Upload request received")
    try:
        if 'files[]' not in request.files:
            logger.error("No file part in the request")
            return jsonify({'error': 'No file part'}), 400

        files = request.files.getlist('files[]')
        if not files or files[0].filename == '':
            logger.error("No selected files")
            return jsonify({'error': 'No selected files'}), 400

        reference_file = request.files.get('reference_file')
        if not reference_file or reference_file.filename == '':
            logger.error("No reference file selected")
            return jsonify({'error': 'No reference file selected'}), 400

        batch_id = str(uuid.uuid4())
        batch_folder = os.path.join(app.config['RESULTS_FOLDER'], batch_id)
        os.makedirs(batch_folder, exist_ok=True)
        logger.info(f"Created batch folder: {batch_folder}")

        parse_doc = request.form.get('parse_doc') == 'true'
        create_summary = request.form.get('create_summary') == 'true'
        min_count = int(request.form.get('min_count', 20))
        max_count = int(request.form.get('max_count', 100))
        parse_level = int(request.form.get('parse_level', 1))

        logger.info(
            f"parse_doc: {parse_doc}, create_summary: {create_summary}, "
            f"min_count: {min_count}, max_count: {max_count}, parse_level: {parse_level}"
        )

        # Save and process reference file
        reference_filename = secure_filename(reference_file.filename)
        reference_path = os.path.join(batch_folder, reference_filename)
        reference_file.save(reference_path)
        keywords = read_keywords(reference_path)
        logger.info(f"Read {len(keywords)} keywords from reference file")

        results = []
        doc_paths = []

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(upload_path)
                doc_paths.append(upload_path)

                logger.info(f"File saved: {upload_path}")

                result = {'filename': filename}
                if parse_doc:
                    logger.info(f"Parsing document: {filename}")
                    doc_folder = parse_docx(upload_path, batch_folder, parse_level, keywords)
                    result['doc_folder'] = os.path.relpath(doc_folder, batch_folder)
                    logger.info(f"Document parsed and saved in: {doc_folder}")

                results.append(result)

        if create_summary:
            logger.info(f"Creating word count summary for all documents")
            summary_file, summary_message = create_word_count_summary(doc_paths, batch_folder, min_count, max_count)
            if summary_file:
                summary_filename = os.path.basename(summary_file)
                results.append({'summary_file': summary_filename})
                logger.info(f"Summary file saved: {summary_file}")
            else:
                logger.warning(summary_message)
            results.append({'summary_message': summary_message})

        logger.info(f"Processing complete. Results: {results}")
        return jsonify({'results': results, 'batch_id': batch_id})

    except Exception as e:
        logger.error(f"An error occurred during file processing: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/download/<batch_id>')
def download_zip(batch_id):
    try:
        batch_folder = os.path.join(app.config['RESULTS_FOLDER'], batch_id)
        if not os.path.exists(batch_folder):
            logger.error(f"Batch folder not found: {batch_folder}")
            return jsonify({'error': 'Batch not found'}), 404

        memory_file = create_zip_file(batch_folder)
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'batch_{batch_id}.zip'
        )
    except Exception as e:
        logger.error(f"An error occurred during zip creation: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/clear', methods=['POST'])
def clear():
    try:
        # Clear upload folder
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        logger.info("Upload folder cleared")
        return jsonify({'message': 'Cleared successfully'})
    except Exception as e:
        logger.error(f"Error clearing upload folder: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(RESULTS_FOLDER, exist_ok=True)
    app.run(debug=True)