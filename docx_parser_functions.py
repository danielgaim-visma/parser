import docx
from collections import defaultdict, Counter
import os
from datetime import datetime
import re
import string
from openpyxl import Workbook

BASE_PATH = "/Users/daniel.gaimvisma.com/PycharmProjects/parsefiles/old_files"
OUTPUT_BASE_PATH = "/Users/daniel.gaimvisma.com/PycharmProjects/parsefiles/parsed_output"


def parse_docx(file_path):
    print(f"Opening document: {file_path}")
    doc = docx.Document(file_path)
    content = defaultdict(lambda: defaultdict(list))
    current_heading1 = "No Heading 1"
    current_heading2 = None

    print(f"Total paragraphs in document: {len(doc.paragraphs)}")
    for i, paragraph in enumerate(doc.paragraphs):
        print(f"Paragraph {i}: Style = {paragraph.style.name}, Text = {paragraph.text[:50]}...")
        if paragraph.style.name == 'Heading 1':
            current_heading1 = paragraph.text
            current_heading2 = None
            print(f"Found Heading 1: {current_heading1}")
        elif paragraph.style.name == 'Heading 2':
            current_heading2 = paragraph.text
            print(f"Found Heading 2: {current_heading2}")
        elif current_heading2 is not None:
            content[current_heading1][current_heading2].append(paragraph)
        elif current_heading1 != "No Heading 1":
            content[current_heading1]["_intro"].append(paragraph)

    print(f"Parsed content structure:")
    for h1, h2_content in content.items():
        print(f"  Heading 1: {h1}")
        for h2, paragraphs in h2_content.items():
            print(f"    Heading 2: {h2}")
            print(f"      Paragraphs: {len(paragraphs)}")

    return dict(content)


def create_output_folder():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"parsed_files_{timestamp}"
    output_folder = os.path.join(OUTPUT_BASE_PATH, folder_name)
    os.makedirs(output_folder, exist_ok=True)
    return output_folder


def sanitize_filename(filename):
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    sanitized = sanitized.replace(' ', '_')
    return sanitized[:255]


def list_docx_files(directory):
    print(f"Listing .docx files in directory: {directory}")
    if not os.path.exists(directory):
        print(f"Directory does not exist: {directory}")
        return []
    docx_files = [f for f in os.listdir(directory) if f.endswith('.docx')]
    print(f"Found {len(docx_files)} .docx files")
    return docx_files


def count_words_in_docx(file_path):
    doc = docx.Document(file_path)
    words = []
    for para in doc.paragraphs:
        words.extend(para.text.lower().split())
    return words


def create_word_count_summary(docx_files, output_folder, min_count, max_count):
    word_count = Counter()
    for file in docx_files:
        file_path = os.path.join(BASE_PATH, file)
        words = count_words_in_docx(file_path)
        word_count.update(words)

    filtered_words = [word for word, count in word_count.items() if min_count <= count <= max_count]
    filtered_words.sort()

    wb = Workbook()
    ws = wb.active
    ws.title = "Word Count Summary"

    ws['A1'] = "Word"
    ws['B1'] = "Count"

    for row, word in enumerate(filtered_words, start=2):
        ws.cell(row=row, column=1, value=word)
        ws.cell(row=row, column=2, value=word_count[word])

    summary_file = os.path.join(output_folder, f"word_count_summary_{min_count}_to_{max_count}.xlsx")
    wb.save(summary_file)
    print(f"Word count summary saved to: {summary_file}")

# No import statements referencing this file