# docx_parser_functions.py

import docx
from collections import defaultdict, Counter
import os
import re


def parse_docx(file_path, output_folder):
    doc = docx.Document(file_path)
    content = defaultdict(lambda: defaultdict(list))
    current_heading1 = "No Heading 1"
    current_heading2 = None

    # Create main folder for the document
    doc_title = os.path.splitext(os.path.basename(file_path))[0]
    doc_folder = os.path.join(output_folder, sanitize_filename(doc_title))
    os.makedirs(doc_folder, exist_ok=True)

    for paragraph in doc.paragraphs:
        if paragraph.style.name == 'Heading 1':
            current_heading1 = paragraph.text
            current_heading2 = None
            # Create folder for Heading 1
            h1_folder = os.path.join(doc_folder, sanitize_filename(current_heading1))
            os.makedirs(h1_folder, exist_ok=True)
        elif paragraph.style.name == 'Heading 2':
            current_heading2 = paragraph.text
            content[current_heading1][current_heading2] = []
        elif current_heading2 is not None:
            content[current_heading1][current_heading2].append(paragraph)
        elif current_heading1 != "No Heading 1":
            content[current_heading1]["_intro"].append(paragraph)

    # Write content to DOCX files
    for h1, h2_content in content.items():
        h1_folder = os.path.join(doc_folder, sanitize_filename(h1))
        for h2, paragraphs in h2_content.items():
            h2_filename = os.path.join(h1_folder, sanitize_filename(h2) + ".docx")
            h2_doc = docx.Document()
            h2_doc.add_heading(h2, level=2)
            for para in paragraphs:
                new_para = h2_doc.add_paragraph()
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
            h2_doc.save(h2_filename)

    return doc_folder


def sanitize_filename(filename):
    return re.sub(r'[^\w\-_\. ]', '_', filename)


def create_word_count_summary(filenames, output_folder, min_count, max_count):
    word_count = Counter()
    for filename in filenames:
        file_path = os.path.join(output_folder, filename)
        if os.path.exists(file_path):
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                words = para.text.lower().split()
                word_count.update(words)

    filtered_words = [word for word, count in word_count.items() if min_count <= count <= max_count]

    if not filtered_words:
        return None  # Return None if no words match the criteria

    summary_filename = f"word_count_summary_{min_count}_to_{max_count}.txt"
    summary_path = os.path.join(output_folder, summary_filename)

    with open(summary_path, 'w', encoding='utf-8') as f:
        for word in sorted(filtered_words):
            f.write(f"{word}: {word_count[word]}\n")

    return summary_path