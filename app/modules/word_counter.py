from collections import Counter
from docx import Document
from openpyxl import Workbook
import os

def create_word_count_summary(doc_paths, output_folder, min_count=20, max_count=100):
    word_count = Counter()

    for doc_path in doc_paths:
        doc = Document(doc_path)
        for para in doc.paragraphs:
            words = para.text.lower().split()
            word_count.update(words)

    filtered_words = {word: count for word, count in word_count.items() if min_count <= count <= max_count}

    if not filtered_words:
        min_count_found = min(word_count.values()) if word_count else 0
        max_count_found = max(word_count.values()) if word_count else 0
        return None, f"No words found with count between {min_count} and {max_count}. Word count range in documents: {min_count_found} - {max_count_found}"

    summary_filename = f"word_count_summary_{min_count}_to_{max_count}.xlsx"
    summary_path = os.path.join(output_folder, summary_filename)

    wb = Workbook()
    ws = wb.active
    ws.title = "Word Count Summary"
    ws.append(["Word", "Count"])
    for word, count in sorted(filtered_words.items(), key=lambda x: x[1], reverse=True):
        ws.append([word, count])
    wb.save(summary_path)

    return summary_path, f"Word count summary created with {len(filtered_words)} words"