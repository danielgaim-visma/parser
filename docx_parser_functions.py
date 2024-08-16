import docx
from collections import defaultdict, Counter
import os
import re
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def parse_docx(file_path, output_folder, parse_level):
    logger.info(f"Parsing document: {file_path}")
    try:
        doc = docx.Document(file_path)
    except Exception as e:
        logger.error(f"Error opening document {file_path}: {str(e)}")
        raise

    content = defaultdict(lambda: defaultdict(list))
    current_headings = [None] * parse_level

    # Create main folder for the document
    doc_title = os.path.splitext(os.path.basename(file_path))[0]
    doc_folder = os.path.join(output_folder, sanitize_filename(doc_title))
    os.makedirs(doc_folder, exist_ok=True)

    for paragraph in doc.paragraphs:
        heading_level = get_heading_level(paragraph)

        if heading_level and heading_level <= parse_level:
            current_headings[heading_level - 1] = paragraph.text
            for i in range(heading_level, parse_level):
                current_headings[i] = None

            # Create folder structure based on headings
            current_folder = doc_folder
            for level in range(heading_level):
                if current_headings[level]:
                    current_folder = os.path.join(current_folder, sanitize_filename(current_headings[level]))
                    os.makedirs(current_folder, exist_ok=True)

        elif all(h is not None for h in current_headings[:parse_level]):
            # Use tuple of headings as key for the outer defaultdict
            content_key = tuple(current_headings[:parse_level - 1])
            # Use the last heading as key for the inner defaultdict
            inner_key = current_headings[parse_level - 1] or "No Heading"
            content[content_key][inner_key].append(paragraph)

    # Write content to DOCX files
    for outer_headings, inner_dict in content.items():
        for inner_heading, paragraphs in inner_dict.items():
            headings = outer_headings + (inner_heading,)
            file_path = os.path.join(doc_folder, *map(sanitize_filename, headings[:-1]))
            file_name = sanitize_filename(headings[-1]) + ".docx"
            full_path = os.path.join(file_path, file_name)

            os.makedirs(file_path, exist_ok=True)

            try:
                doc = docx.Document()
                for heading in headings:
                    doc.add_heading(heading, level=headings.index(heading) + 1)

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

                doc.save(full_path)
                logger.info(f"Saved parsed content to: {full_path}")
            except Exception as e:
                logger.error(f"Error saving document {full_path}: {str(e)}")

    logger.info(f"Parsing complete. Output folder: {doc_folder}")
    return doc_folder


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


def create_word_count_summary(filenames, output_folder, min_count, max_count):
    logger.info("Creating word count summary")
    word_count = Counter()
    for filename in filenames:
        file_path = os.path.join(output_folder, filename)
        if os.path.exists(file_path):
            try:
                doc = docx.Document(file_path)
                for para in doc.paragraphs:
                    words = para.text.lower().split()
                    word_count.update(words)
            except Exception as e:
                logger.error(f"Error processing file {file_path} for word count: {str(e)}")

    filtered_words = [word for word, count in word_count.items() if min_count <= count <= max_count]

    if not filtered_words:
        logger.warning("No words match the specified count range")
        return None

    summary_filename = f"word_count_summary_{min_count}_to_{max_count}.txt"
    summary_path = os.path.join(output_folder, summary_filename)

    try:
        with open(summary_path, 'w', encoding='utf-8') as f:
            for word in sorted(filtered_words):
                f.write(f"{word}: {word_count[word]}\n")
        logger.info(f"Word count summary saved to: {summary_path}")
    except Exception as e:
        logger.error(f"Error writing word count summary: {str(e)}")
        return None

    return summary_path