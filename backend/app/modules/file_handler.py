import os
import uuid
import zipfile
import io
from werkzeug.utils import secure_filename
from flask import current_app

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_uploaded_file(file, folder):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(folder, filename)
        file.save(file_path)
        return file_path
    return None

def create_batch_folder():
    batch_id = str(uuid.uuid4())
    batch_folder = os.path.join(current_app.config['RESULTS_FOLDER'], batch_id)
    os.makedirs(batch_folder, exist_ok=True)
    return batch_id, batch_folder

def create_zip_file(batch_folder, files_to_zip, zip_filename):
    zip_path = os.path.join(batch_folder, zip_filename)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in files_to_zip:
            file_path = os.path.join(batch_folder, file)
            if os.path.exists(file_path):
                zf.write(file_path, file)
    return zip_path

def clear_upload_folder():
    upload_folder = current_app.config['UPLOAD_FOLDER']
    for filename in os.listdir(upload_folder):
        file_path = os.path.join(upload_folder, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)
    return True