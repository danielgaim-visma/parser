import os
import uuid
import zipfile
import io
import traceback
from werkzeug.utils import secure_filename
from flask import current_app


def allowed_file(filename):
    try:
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
    except Exception as e:
        current_app.logger.error(f"Error in allowed_file function: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return False


def save_uploaded_file(file, folder):
    try:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(folder, filename)
            file.save(file_path)
            current_app.logger.info(f"File saved successfully: {file_path}")
            return file_path
        else:
            current_app.logger.warning(f"Invalid file: {file.filename if file else 'No file'}")
            return None
    except Exception as e:
        current_app.logger.error(f"Error saving uploaded file: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return None


def create_batch_folder():
    try:
        batch_id = str(uuid.uuid4())
        batch_folder = os.path.join(current_app.config['RESULTS_FOLDER'], batch_id)
        os.makedirs(batch_folder, exist_ok=True)
        current_app.logger.info(f"Created batch folder: {batch_folder}")
        return batch_id, batch_folder
    except Exception as e:
        current_app.logger.error(f"Error creating batch folder: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        raise


def create_zip_file(batch_folder, files_to_zip, zip_filename):
    zip_path = os.path.join(batch_folder, zip_filename)
    current_app.logger.info(f"Creating zip file at: {zip_path}")
    current_app.logger.info(f"Files to zip: {files_to_zip}")

    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file in files_to_zip:
                file_path = os.path.join(batch_folder, file)
                if os.path.exists(file_path):
                    current_app.logger.info(f"Adding file to zip: {file_path}")
                    zf.write(file_path, file)
                else:
                    current_app.logger.warning(f"File not found: {file_path}")

        if os.path.exists(zip_path):
            current_app.logger.info(f"Zip file created successfully: {zip_path}")
        else:
            current_app.logger.error(f"Failed to create zip file: {zip_path}")
    except zipfile.BadZipFile as e:
        current_app.logger.error(f"BadZipFile error: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        raise
    except zipfile.LargeZipFile as e:
        current_app.logger.error(f"LargeZipFile error: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        raise
    except Exception as e:
        current_app.logger.error(f"Unexpected error creating zip file: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        raise

    return zip_path


def clear_upload_folder():
    upload_folder = current_app.config['UPLOAD_FOLDER']
    current_app.logger.info(f"Clearing upload folder: {upload_folder}")
    files_removed = 0
    errors = 0

    try:
        for filename in os.listdir(upload_folder):
            file_path = os.path.join(upload_folder, filename)
            if os.path.isfile(file_path):
                try:
                    os.unlink(file_path)
                    files_removed += 1
                    current_app.logger.info(f"Removed file: {file_path}")
                except Exception as e:
                    errors += 1
                    current_app.logger.error(f"Error removing file {file_path}: {str(e)}")
                    current_app.logger.error(traceback.format_exc())

        current_app.logger.info(f"Removed {files_removed} files from upload folder")
        if errors > 0:
            current_app.logger.warning(f"Encountered {errors} errors while clearing upload folder")
        return True
    except Exception as e:
        current_app.logger.error(f"Error clearing upload folder: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return False


def get_file_size(file_path):
    try:
        size = os.path.getsize(file_path)
        current_app.logger.info(f"File size of {file_path}: {size} bytes")
        return size
    except Exception as e:
        current_app.logger.error(f"Error getting file size for {file_path}: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return None


def check_disk_space(folder):
    try:
        total, used, free = shutil.disk_usage(folder)
        current_app.logger.info(f"Disk space for {folder}: total={total}, used={used}, free={free}")
        return free
    except Exception as e:
        current_app.logger.error(f"Error checking disk space for {folder}: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return None