from flask import Blueprint, request, jsonify, current_app
import os
import logging
from ..modules.file_handler import allowed_file, save_uploaded_file, create_batch_folder, clear_upload_folder, create_zip_file
from ..modules.document_parser import parse_multiple_docx
from ..modules.keyword_tagger import read_keywords, tag_multiple_documents
from ..modules.word_counter import create_word_count_summary

logger = logging.getLogger(__name__)

upload = Blueprint('upload', __name__)

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
        keyword_tag = request.form.get('keywordTag') == 'true'

        logger.info(f"parse_doc: {parse_doc}, create_summary: {create_summary}, keyword_tag: {keyword_tag}")

        if not parse_doc and not create_summary and not keyword_tag:
            logger.error("No operation selected")
            return jsonify({'error': 'Please select at least one operation (Parse Documents, Create Summary, or Keyword Tag)'}), 400

        batch_id, batch_folder = create_batch_folder()
        logger.info(f"Created batch folder: {batch_folder}")

        min_count = int(request.form.get('minCount', 0))
        max_count = int(request.form.get('maxCount', 300))
        parse_level = int(request.form.get('parseLevel', 1))

        logger.info(
            f"parse_doc: {parse_doc}, create_summary: {create_summary}, keyword_tag: {keyword_tag}, "
            f"min_count: {min_count}, max_count: {max_count}, parse_level: {parse_level}"
        )

        keywords = []
        reference_file = request.files.get('referenceFile')
        if reference_file and reference_file.filename != '':
            try:
                reference_filename = save_uploaded_file(reference_file, batch_folder)
                if reference_filename:
                    keywords = read_keywords(reference_filename)
                    logger.info(f"Read {len(keywords)} keywords from reference file")
                else:
                    logger.warning("Invalid reference file")
            except Exception as e:
                logger.error(f"Error processing reference file: {str(e)}")
                return jsonify({'error': f"Error processing reference file: {str(e)}"}), 400

        results = []
        doc_paths = []
        files_to_zip = []

        for file in files:
            if file and allowed_file(file.filename):
                try:
                    filename = save_uploaded_file(file, current_app.config['UPLOAD_FOLDER'])
                    if filename:
                        doc_paths.append(filename)
                        logger.info(f"File saved: {filename}")
                except Exception as e:
                    logger.error(f"Error saving file {file.filename}: {str(e)}")
                    return jsonify({'error': f"Error saving file {file.filename}: {str(e)}"}), 500

        if parse_doc:
            logger.info(f"Parsing documents: {doc_paths}")
            try:
                parsed_results = parse_multiple_docx(doc_paths, batch_folder, parse_level, keywords if keyword_tag else None)
                results.extend(parsed_results)
                files_to_zip.extend([result['output_file'] for result in parsed_results if 'output_file' in result])
                logger.info(f"Parsed {len(parsed_results)} documents")
            except Exception as e:
                logger.error(f"Error parsing documents: {str(e)}")
                return jsonify({'error': f"Error parsing documents: {str(e)}"}), 500

        if create_summary:
            logger.info(f"Creating word count summary for all documents")
            try:
                summary_file, summary_message = create_word_count_summary(doc_paths, batch_folder, min_count, max_count)
                if summary_file:
                    summary_filename = os.path.basename(summary_file)
                    results.append({'summary_file': summary_filename})
                    files_to_zip.append(summary_filename)
                    logger.info(f"Summary file saved: {summary_file}")
                else:
                    logger.warning(summary_message)
                results.append({'summary_message': summary_message})
            except Exception as e:
                logger.error(f"Error creating word count summary: {str(e)}")
                return jsonify({'error': f"Error creating word count summary: {str(e)}"}), 500

        if keyword_tag:
            logger.info(f"Tagging documents with keywords: {doc_paths}")
            try:
                tagged_results = tag_multiple_documents(doc_paths, batch_folder, keywords)
                results.extend(tagged_results)
                files_to_zip.extend([result['output_file'] for result in tagged_results if 'output_file' in result])
                logger.info(f"Tagged {len(tagged_results)} documents")
            except Exception as e:
                logger.error(f"Error tagging documents with keywords: {str(e)}")
                return jsonify({'error': f"Error tagging documents with keywords: {str(e)}"}), 500

        logger.info(f"Processing complete. Results: {results}")

        # Create a single zip file for all processed files
        if files_to_zip:
            try:
                zip_filename = "processed_documents.zip"
                zip_path = create_zip_file(batch_folder, files_to_zip, zip_filename)

                # Prepare the response
                processed_folders = [{
                    'output_folder': 'All Processed Documents',
                    'zipUrl': f'/api/download/{batch_id}/{zip_filename}'
                }]
                logger.info(f"Zip file created: {zip_path}")
            except Exception as e:
                logger.error(f"Error in zip file creation: {str(e)}")
                return jsonify({'error': f"Error in zip file creation: {str(e)}"}), 500
        else:
            logger.warning("No files to zip")
            processed_folders = []

        return jsonify({
            'batchId': batch_id,
            'message': 'Processing completed successfully.',
            'processedFolders': processed_folders,
            'results': results
        }), 200

    except Exception as e:
        logger.exception(f"An unexpected error occurred during file processing: {str(e)}")
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