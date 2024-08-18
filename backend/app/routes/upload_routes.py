from flask import Blueprint, request, jsonify, current_app
import os
import logging
import traceback
from ..modules.file_handler import allowed_file, save_uploaded_file, create_batch_folder, clear_upload_folder, create_zip_file, get_file_size, check_disk_space
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

        # Check available disk space
        free_space = check_disk_space(batch_folder)
        if free_space is not None and free_space < 1000000000:  # Less than 1GB
            logger.warning(f"Low disk space. Only {free_space} bytes available.")

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
                logger.error(traceback.format_exc())
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
                        file_size = get_file_size(filename)
                        logger.info(f"File saved: {filename}, Size: {file_size} bytes")
                except Exception as e:
                    logger.error(f"Error saving file {file.filename}: {str(e)}")
                    logger.error(traceback.format_exc())
                    return jsonify({'error': f"Error saving file {file.filename}: {str(e)}"}), 500

        if parse_doc:
            logger.info(f"Parsing documents: {doc_paths}")
            try:
                parsed_results = parse_multiple_docx(doc_paths, batch_folder, parse_level, keywords if keyword_tag else None)
                results.extend(parsed_results)
                for result in parsed_results:
                    if 'output_folder' in result:
                        for root, dirs, files in os.walk(result['output_folder']):
                            for file in files:
                                relative_path = os.path.relpath(os.path.join(root, file), batch_folder)
                                files_to_zip.append(relative_path)
                logger.info(f"Added {len(files_to_zip)} files to zip list from parsing")
            except Exception as e:
                logger.error(f"Error parsing documents: {str(e)}")
                logger.error(traceback.format_exc())
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
                logger.error(traceback.format_exc())
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
                logger.error(traceback.format_exc())
                return jsonify({'error': f"Error tagging documents with keywords: {str(e)}"}), 500

        logger.info(f"Processing complete. Results: {results}")
        logger.info(f"Files to zip: {files_to_zip}")

        if files_to_zip:
            try:
                zip_filename = "processed_documents.zip"
                logger.info(f"Creating zip file: {zip_filename}")
                zip_path = create_zip_file(batch_folder, files_to_zip, zip_filename)
                zip_size = get_file_size(zip_path)
                logger.info(f"Zip file created: {zip_path}, Size: {zip_size} bytes")

                processed_folders = [{
                    'output_folder': 'All Processed Documents',
                    'zipUrl': f'/api/download/{batch_id}/{zip_filename}'
                }]
            except Exception as e:
                logger.error(f"Error in zip file creation: {str(e)}")
                logger.error(traceback.format_exc())
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
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@upload.route('/api/clear', methods=['POST'])
def clear():
    try:
        success = clear_upload_folder()
        if success:
            logger.info("Upload folder cleared successfully")
            return jsonify({'message': 'Cleared successfully'})
        else:
            logger.error("Failed to clear upload folder")
            return jsonify({'error': 'Failed to clear upload folder'}), 500
    except Exception as e:
        logger.error(f"Error clearing upload folder: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500