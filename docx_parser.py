import docx
from collections import defaultdict
import os
from datetime import datetime
import re

BASE_PATH = "/Users/daniel.gaimvisma.com/pycharprojects/parsefiles/old_files"
OUTPUT_BASE_PATH = "/Users/daniel.gaimvisma.com/pycharprojects/parsefiles/parsed_output"

def parse_docx(file_path):
    doc = docx.Document(file_path)
    content = defaultdict(lambda: defaultdict(list))
    current_heading1 = "No Overskrift 1"
    current_heading2 = None

    for paragraph in doc.paragraphs:
        if paragraph.style.name == 'Overskrift 1':
            current_heading1 = paragraph.text
            current_heading2 = None
        elif paragraph.style.name == 'Overskrift 2':
            current_heading2 = paragraph.text
        elif current_heading2 is not None:
            content[current_heading1][current_heading2].append(paragraph.text)
        elif current_heading1 != "No Overskrift 1":
            content[current_heading1]["_intro"].append(paragraph.text)

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
                file_name = f"{base_name}_intro.txt"
            else:
                file_name = f"{base_name}_{sanitize_filename(heading2)}.txt"

            output_file = os.path.join(heading1_folder, file_name)

            with open(output_file, 'w', encoding='utf-8') as f:
                if heading2 != "_intro":
                    f.write(f"Overskrift 2: {heading2}\n\n")
                for paragraph in paragraphs:
                    f.write(f"{paragraph}\n")

    return output_folder

def list_docx_files(directory):
    docx_files = [f for f in os.listdir(directory) if f.endswith('.docx')]
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

    docx_files = list_docx_files(BASE_PATH)

    if not docx_files:
        print(f"No .docx files found in {BASE_PATH}")
        return

    selected_file = select_file(docx_files)
    file_path = os.path.join(BASE_PATH, selected_file)

    try:
        parsed_content = parse_docx(file_path)
        if not parsed_content:
            print("No content found in the document.")
        else:
            output_folder = create_output_folder()
            saved_folder = save_parsed_content(parsed_content, output_folder, selected_file)
            print(f"\nParsed content has been saved to: {saved_folder}")
            print("\nContent overview:")
            for heading1, heading2_content in parsed_content.items():
                print(f"\nOverskrift 1: {heading1}")
                for heading2, paragraphs in heading2_content.items():
                    if heading2 == "_intro":
                        print(f"  Introduction: {len(paragraphs)} paragraphs")
                    else:
                        print(f"  Overskrift 2: {heading2}")
                        print(f"    {len(paragraphs)} paragraphs")
    except Exception as e:
        print(f"An error occurred while processing the file: {e}")

if __name__ == "__main__":
    main()


def sanitize_filename(filename):
    # Remove or replace characters that are invalid in filenames
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    # Trim to a reasonable length (e.g., 255 characters)
    return sanitized[:255]


def save_parsed_content(parsed_content, output_folder, original_filename):
    base_name = os.path.splitext(original_filename)[0]

    for heading1, heading2_content in parsed_content.items():
        heading1_folder = os.path.join(output_folder, sanitize_filename(heading1))
        os.makedirs(heading1_folder, exist_ok=True)

        for heading2, paragraphs in heading2_content.items():
            if heading2 == "_intro":
                file_name = f"{base_name}_intro.txt"
            else:
                file_name = f"{base_name}_{sanitize_filename(heading2)}.txt"

            output_file = os.path.join(heading1_folder, file_name)

            with open(output_file, 'w', encoding='utf-8') as f:
                if heading2 != "_intro":
                    f.write(f"Overskrift 2: {heading2}\n\n")
                for paragraph in paragraphs:
                    f.write(f"{paragraph}\n")

    return output_folder


def main():
    print(f"Documents will be read from: {BASE_PATH}")
    filename = input("Enter the name of the docx file (e.g., 'document.docx'): ")
    file_path = os.path.join(BASE_PATH, filename)

    if not os.path.exists(file_path):
        print(f"Error: File '{filename}' not found in {BASE_PATH}")
        return

    try:
        parsed_content = parse_docx(file_path)
        if not parsed_content:
            print("No content found in the document.")
        else:
            output_folder = create_output_folder()
            saved_folder = save_parsed_content(parsed_content, output_folder, filename)
            print(f"\nParsed content has been saved to: {saved_folder}")
            print("\nContent overview:")
            for heading1, heading2_content in parsed_content.items():
                print(f"\nOverskrift 1: {heading1}")
                for heading2, paragraphs in heading2_content.items():
                    if heading2 == "_intro":
                        print(f"  Introduction: {len(paragraphs)} paragraphs")
                    else:
                        print(f"  Overskrift 2: {heading2}")
                        print(f"    {len(paragraphs)} paragraphs")
    except Exception as e:
        print(f"An error occurred while processing the file: {e}")


if __name__ == "__main__":
    main()