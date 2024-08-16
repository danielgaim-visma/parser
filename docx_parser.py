import docx
from collections import defaultdict
import os
from datetime import datetime
import re

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


def save_parsed_content(parsed_content, output_folder, original_filename):
    base_name = os.path.splitext(original_filename)[0]

    for heading1, heading2_content in parsed_content.items():
        heading1_folder = os.path.join(output_folder, sanitize_filename(heading1))
        os.makedirs(heading1_folder, exist_ok=True)

        for heading2, paragraphs in heading2_content.items():
            if heading2 == "_intro":
                file_name = f"{base_name}_intro.docx"
            else:
                file_name = f"{base_name}_{sanitize_filename(heading2)}.docx"

            output_file = os.path.join(heading1_folder, file_name)

            doc = docx.Document()
            if heading2 != "_intro":
                doc.add_heading(heading2, level=2)
            for paragraph in paragraphs:
                doc.add_paragraph(paragraph.text, style=paragraph.style)

            doc.save(output_file)

    return output_folder


def list_docx_files(directory):
    print(f"Listing .docx files in directory: {directory}")
    if not os.path.exists(directory):
        print(f"Directory does not exist: {directory}")
        return []
    docx_files = [f for f in os.listdir(directory) if f.endswith('.docx')]
    print(f"Found {len(docx_files)} .docx files")
    return docx_files


def select_file(files):
    print("\nAvailable .docx files:")
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")

    while True:
        try:
            choice = int(input("\nEnter the number of the file you want to parse: "))
            if 1 <= choice <= len(files):
                return files[choice - 1]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")


def main():
    print(f"Documents will be read from: {BASE_PATH}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"BASE_PATH exists: {os.path.exists(BASE_PATH)}")

    docx_files = list_docx_files(BASE_PATH)

    if not docx_files:
        print(f"No .docx files found in {BASE_PATH}")
        return

    selected_file = select_file(docx_files)
    file_path = os.path.join(BASE_PATH, selected_file)

    try:
        parsed_content = parse_docx(file_path)
        if not parsed_content:
            print("No content found in the document. This could be because:")
            print("1. The document is empty")
            print("2. The document doesn't use 'Heading 1' or 'Heading 2' styles")
            print("3. There's an issue with reading the document styles")
        else:
            output_folder = create_output_folder()
            saved_folder = save_parsed_content(parsed_content, output_folder, selected_file)
            print(f"\nParsed content has been saved to: {saved_folder}")
            print("\nContent overview:")
            for heading1, heading2_content in parsed_content.items():
                print(f"\nHeading 1: {heading1}")
                for heading2, paragraphs in heading2_content.items():
                    if heading2 == "_intro":
                        print(f"  Introduction: {len(paragraphs)} paragraphs")
                    else:
                        print(f"  Heading 2: {heading2}")
                        print(f"    {len(paragraphs)} paragraphs")
    except Exception as e:
        print(f"An error occurred while processing the file: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()