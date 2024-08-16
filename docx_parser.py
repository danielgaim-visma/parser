import docx
from collections import defaultdict, Counter
import os
from datetime import datetime
import re
import string

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
            choice = int(input("\nEnter the number of the file you want to parse (0 to process all files): "))
            if choice == 0:
                return files
            elif 1 <= choice <= len(files):
                return [files[choice - 1]]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")


def count_words_in_docx(file_path):
    doc = docx.Document(file_path)
    words = []
    for para in doc.paragraphs:
        words.extend(para.text.lower().split())
    return words


def create_word_count_summary(docx_files, output_folder):
    word_count = Counter()
    for file in docx_files:
        file_path = os.path.join(BASE_PATH, file)
        words = count_words_in_docx(file_path)
        word_count.update(words)

    common_words = [word for word, count in word_count.items() if count > 20]
    common_words.sort()

    summary_doc = docx.Document()
    summary_doc.add_heading('Word Count Summary', level=1)
    for word in common_words:
        summary_doc.add_paragraph(f"{word}: {word_count[word]}")

    summary_file = os.path.join(output_folder, "word_count_summary.docx")
    summary_doc.save(summary_file)
    print(f"Word count summary saved to: {summary_file}")


def main():
    print(f"Documents will be read from: {BASE_PATH}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"BASE_PATH exists: {os.path.exists(BASE_PATH)}")

    all_docx_files = list_docx_files(BASE_PATH)

    if not all_docx_files:
        print(f"No .docx files found in {BASE_PATH}")
        return

    selected_files = select_file(all_docx_files)
    output_folder = create_output_folder()

    try:
        for file in selected_files:
            file_path = os.path.join(BASE_PATH, file)
            parsed_content = parse_docx(file_path)
            if not parsed_content:
                print(f"No content found in the document: {file}")
            else:
                saved_folder = save_parsed_content(parsed_content, output_folder, file)
                print(f"\nParsed content for {file} has been saved to: {saved_folder}")
                print("\nContent overview:")
                for heading1, heading2_content in parsed_content.items():
                    print(f"\nHeading 1: {heading1}")
                    for heading2, paragraphs in heading2_content.items():
                        if heading2 == "_intro":
                            print(f"  Introduction: {len(paragraphs)} paragraphs")
                        else:
                            print(f"  Heading 2: {heading2}")
                            print(f"    {len(paragraphs)} paragraphs")

        # Create word count summary
        create_word_count_summary(selected_files, output_folder)

    except Exception as e:
        print(f"An error occurred while processing the file(s): {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()