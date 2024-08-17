from flask import Blueprint, request, jsonify, current_app
import os
import logging
from ..modules.file_handler import allowed_file, save_uploaded_file, create_batch_folder
from ..modules.document_parser import parse_multiple_docx
from ..modules.keyword_tagger import read_keywords
from ..modules.word_counter import create_word_count_summary

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

upload = Blueprint('upload', __name__)

@upload.route('/upload', methods=['POST'])
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

        # Log all form data
        logger.info(f"Received form data: {request.form}")

        parse_doc = request.form.get('parse_doc') == 'true'
        create_summary = request.form.get('create_summary') == 'true'

        logger.info(f"parse_doc: {parse_doc}, create_summary: {create_summary}")

        if not parse_doc and not create_summary:
            logger.error("No operation selected")
            return jsonify({'error': 'Please select at least one operation (Parse Documents or Create Summary)'}), 400

        batch_id, batch_folder = create_batch_folder()
        logger.info(f"Created batch folder: {batch_folder}")

        min_count = int(request.form.get('min_count', 20))
        max_count = int(request.form.get('max_count', 100))
        parse_level = int(request.form.get('parse_level', 1))

        logger.info(
            f"parse_doc: {parse_doc}, create_summary: {create_summary}, "
            f"min_count: {min_count}, max_count: {max_count}, parse_level: {parse_level}"
        )

        keywords = []
        reference_file = request.files.get('reference_file')
        if reference_file and reference_file.filename != '':
            reference_filename = save_uploaded_file(reference_file, batch_folder)
            if reference_filename:
                keywords = read_keywords(reference_filename)
                logger.info(f"Read {len(keywords)} keywords from reference file")
            else:
                logger.warning("Invalid reference file")
        else:
            logger.info("No reference file provided")

        results = []
        doc_paths = []

        for file in files:
            if file and allowed_file(file.filename):
                filename = save_uploaded_file(file, current_app.config['UPLOAD_FOLDER'])
                if filename:
                    doc_paths.append(filename)
                    logger.info(f"File saved: {filename}")

        if parse_doc:
            logger.info(f"Parsing documents: {doc_paths}")
            parsed_results = parse_multiple_docx(doc_paths, batch_folder, parse_level, keywords)
            results.extend(parsed_results)

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

@upload.route('/clear', methods=['POST'])
def clear():
    try:
        # Clear upload folder
        for filename in os.listdir(current_app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        logger.info("Upload folder cleared")
        return jsonify({'message': 'Cleared successfully'})
    except Exception as e:
        logger.error(f"Error clearing upload folder: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500