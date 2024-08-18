import os
import re
from docx import Document
from collections import OrderedDict
import logging
from .keyword_tagger import tag_document
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def parse_multiple_docx(file_paths, output_folder, parse_level, keywords):
    results = []
    with ThreadPoolExecutor() as executor:
        future_to_file = {executor.submit(parse_docx, file_path, output_folder, parse_level, keywords): file_path for file_path in file_paths}
        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                doc_folder = future.result()
                results.append({"file": os.path.basename(file_path), "output_folder": doc_folder})
            except Exception as exc:
                logger.error(f'{file_path} generated an exception: {exc}')
                results.append({"file": os.path.basename(file_path), "error": str(exc)})
    return results

def parse_docx(file_path, output_folder, parse_level, keywords):
    logger.info(f"Parsing document: {file_path}")
    try:
        doc = Document(file_path)
    except Exception as e:
        logger.error(f"Error opening document {file_path}: {str(e)}")
        raise

    content = OrderedDict()
    current_headings = [''] * parse_level
    current_content = []

    def save_current_content():
        if any(current_headings):
            current_dict = content
            for level, heading in enumerate(current_headings):
                if heading:
                    if heading not in current_dict:
                        current_dict[heading] = OrderedDict()
                    if level == parse_level - 1:
                        if current_content:
                            current_dict[heading] = current_content.copy()
                        break
                    current_dict = current_dict[heading]
            current_content.clear()

    for paragraph in doc.paragraphs:
        heading_level = get_heading_level(paragraph)

        if heading_level is not None and heading_level <= parse_level:
            save_current_content()
            current_headings[heading_level - 1] = paragraph.text.strip()
            for i in range(heading_level, parse_level):
                current_headings[i] = ''
        else:
            if paragraph.text.strip():
                current_content.append(paragraph)

    save_current_content()

    # Create main folder for the document
    doc_title = os.path.splitext(os.path.basename(file_path))[0]
    doc_folder = os.path.join(output_folder, sanitize_filename(doc_title))
    os.makedirs(doc_folder, exist_ok=True)

    # Write content to DOCX files
    write_content_to_files(content, doc_folder, parse_level, keywords)

    logger.info(f"Parsing complete. Output folder: {doc_folder}")
    return doc_folder

def write_content_to_files(content, folder, parse_level, keywords, parent_path=''):
    for heading, subcontent in content.items():
        current_path = os.path.join(parent_path, sanitize_filename(heading))
        current_folder = os.path.join(folder, current_path)

        if isinstance(subcontent, OrderedDict):
            os.makedirs(current_folder, exist_ok=True)
            write_content_to_files(subcontent, folder, parse_level - 1, keywords, current_path)
        elif subcontent:  # Only create a file if there's content
            os.makedirs(os.path.dirname(current_folder), exist_ok=True)
            file_name = f"{sanitize_filename(heading)}.docx"
            full_path = os.path.join(folder, f"{current_path}.docx")
            save_docx(full_path, heading, subcontent, parse_level)
            if keywords:
                tag_document(full_path, keywords)
            logger.info(f"Saved parsed content to: {full_path}")

def save_docx(full_path, heading, content, parse_level):
    try:
        doc = Document()
        doc.add_heading(heading, level=parse_level)
        add_paragraphs(doc, content)
        doc.save(full_path)
    except Exception as e:
        logger.error(f"Error saving document {full_path}: {str(e)}")

def add_paragraphs(doc, paragraphs):
    for para in paragraphs:
        new_para = doc.add_paragraph()
        new_para.style = para.style
        new_para.text = para.text
        # Copy runs to preserve formatting
        new_para.runs.clear()
        for run in para.runs:
            new_run = new_para.add_run(run.text)
            new_run.bold = run.bold
            new_run.italic = run.italic
            new_run.underline = run.underline
            # Add more formatting attributes as needed

def get_heading_level(paragraph):
    if paragraph.style.name.startswith('Heading'):
        try:
            return int(paragraph.style.name.split()[-1])
        except ValueError:
            logger.warning(f"Invalid heading style: {paragraph.style.name}")
    return None

def sanitize_filename(filename):
    # Remove invalid characters and limit length
    sanitized = re.sub(r'[^\w\-_\. ]', '_', filename)
    return sanitized[:255]  # Limit to 255 characters