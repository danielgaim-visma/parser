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