from flask import Blueprint, request, jsonify, current_app
import os
import logging
import zipfile
from ..modules.file_handler import allowed_file, save_uploaded_file, create_batch_folder, clear_upload_folder
from ..modules.document_parser import parse_multiple_docx
from ..modules.keyword_tagger import read_keywords
from ..modules.word_counter import create_word_count_summary

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

upload = Blueprint('upload', __name__)

def create_zip_file(batch_folder, output_folders, zip_filename):
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for folder in output_folders:
            folder_name = os.path.basename(folder)
            for root, dirs, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.join(folder_name, os.path.relpath(file_path, folder))
                    zipf.write(file_path, arcname)

@upload.route('/api/upload', methods=['POST'])
def upload_file():
    logger.info("Upload request received")
    try:
        if 'files' not in request.files:
            logger.error("No file part in the request")
            return jsonify({'error': 'No file part'}), 400

        files = request.files.getlist('files')
        if not files or files[0].filename == '':
            logger.error("No selected files")
            return jsonify({'error': 'No selected files'}), 400

        logger.info(f"Received form data: {request.form}")

        parse_doc = request.form.get('parseDoc') == 'true'
        create_summary = request.form.get('createSummary') == 'true'

        logger.info(f"parse_doc: {parse_doc}, create_summary: {create_summary}")

        if not parse_doc and not create_summary:
            logger.error("No operation selected")
            return jsonify({'error': 'Please select at least one operation (Parse Documents or Create Summary)'}), 400

        batch_id, batch_folder = create_batch_folder()
        logger.info(f"Created batch folder: {batch_folder}")

        min_count = int(request.form.get('minCount')) if request.form.get('minCount') else 20
        max_count = int(request.form.get('maxCount')) if request.form.get('maxCount') else 100
        parse_level = int(request.form.get('parseLevel', 1))

        logger.info(
            f"parse_doc: {parse_doc}, create_summary: {create_summary}, "
            f"min_count: {min_count}, max_count: {max_count}, parse_level: {parse_level}"
        )

        keywords = []
        reference_file = request.files.get('referenceFile')
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

        # Create a single zip file for all processed folders
        output_folders = [result['output_folder'] for result in results if 'output_folder' in result]
        zip_filename = "processed_documents.zip"
        zip_path = os.path.join(batch_folder, zip_filename)
        create_zip_file(batch_folder, output_folders, zip_path)

        # Prepare the response
        processed_folders = [{
            'output_folder': 'All Processed Documents',
            'zipUrl': f'/api/download/{batch_id}/{zip_filename}'
        }]

        return jsonify({
            'batchId': batch_id,
            'message': 'Processing completed successfully.',
            'processedFolders': processed_folders
        }), 200

    except Exception as e:
        logger.error(f"An error occurred during file processing: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@upload.route('/api/clear', methods=['POST'])
def clear():
    try:
        clear_upload_folder()
        logger.info("Upload folder cleared")
        return jsonify({'message': 'Cleared successfully'})
    except Exception as e:
        logger.error(f"Error clearing upload folder: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500