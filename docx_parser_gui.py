import sys
import os
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QFileDialog, QMessageBox, QProgressBar
from PyQt5.QtCore import Qt, QThread, pyqtSignal, PYQT_VERSION_STR
from importlib import import_module

# Set up logging
logging.basicConfig(filename='docx_parser_gui.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Function to check and log system information
def log_system_info():
    logging.info(f"Python version: {sys.version}")
    logging.info(f"PyQt5 version: {PYQT_VERSION_STR}")
    logging.info(f"Operating System: {os.name}")
    logging.info(f"Current working directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    print(f"PyQt5 version: {PYQT_VERSION_STR}")
    print(f"Operating System: {os.name}")
    print(f"Current working directory: {os.getcwd()}")

log_system_info()

# Dynamically import required functions
try:
    docx_parser_functions = import_module('docx_parser_functions')
    parse_docx = docx_parser_functions.parse_docx
    create_word_count_summary = docx_parser_functions.create_word_count_summary
    create_output_folder = docx_parser_functions.create_output_folder
    list_docx_files = docx_parser_functions.list_docx_files
    logging.info("Successfully imported functions from docx_parser_functions")
except ImportError as e:
    logging.error(f"Error importing from docx_parser_functions: {e}")
    print(f"Error importing from docx_parser_functions: {e}")
    sys.exit(1)

class WorkerThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, file_path, parse_doc, create_summary, min_count, max_count):
        super().__init__()
        self.file_path = file_path
        self.parse_doc = parse_doc
        self.create_summary = create_summary
        self.min_count = min_count
        self.max_count = max_count

    def run(self):
        try:
            output_folder = create_output_folder()
            logging.info(f"Created output folder: {output_folder}")

            if self.parse_doc:
                parsed_content = parse_docx(self.file_path)
                if parsed_content:
                    logging.info("Document parsed successfully")
                else:
                    self.error.emit("No content found in the document.")
                    return

            if self.create_summary:
                create_word_count_summary([os.path.basename(self.file_path)], output_folder, self.min_count, self.max_count)
                logging.info("Word count summary created successfully")

            self.finished.emit(f"Processing complete. Output saved in {output_folder}")
        except Exception as e:
            self.error.emit(f"An error occurred: {str(e)}")
            logging.exception("Error during processing")

class DocxParserGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('DOCX Parser')
        self.setGeometry(100, 100, 600, 400)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # File selection
        file_layout = QHBoxLayout()
        self.file_path = QLineEdit()
        file_layout.addWidget(QLabel('Select DOCX file:'))
        file_layout.addWidget(self.file_path)
        browse_button = QPushButton('Browse')
        browse_button.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_button)
        layout.addLayout(file_layout)

        # Checkboxes
        self.parse_checkbox = QCheckBox('Parse document')
        self.parse_checkbox.setChecked(True)
        layout.addWidget(self.parse_checkbox)

        self.word_count_checkbox = QCheckBox('Create word count summary')
        layout.addWidget(self.word_count_checkbox)

        # Word count range
        count_layout = QHBoxLayout()
        self.min_count = QLineEdit('5')
        self.max_count = QLineEdit('80')
        count_layout.addWidget(QLabel('Min word count:'))
        count_layout.addWidget(self.min_count)
        count_layout.addWidget(QLabel('Max word count:'))
        count_layout.addWidget(self.max_count)
        layout.addLayout(count_layout)

        # Process button
        self.process_button = QPushButton('Process')
        self.process_button.clicked.connect(self.process)
        layout.addWidget(self.process_button)

        # Progress bar
        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        # Status bar
        self.statusBar().showMessage('Ready')

    def browse_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select DOCX file", "", "DOCX Files (*.docx)")
        if file_name:
            self.file_path.setText(file_name)
            logging.info(f"Selected file: {file_name}")

    def process(self):
        file_path = self.file_path.text()
        if not file_path:
            QMessageBox.warning(self, "Error", "Please select a DOCX file.")
            return

        try:
            min_count = int(self.min_count.text())
            max_count = int(self.max_count.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter valid numbers for min and max word count.")
            return

        self.progress.setRange(0, 0)  # Indeterminate progress
        self.statusBar().showMessage('Processing...')
        self.process_button.setEnabled(False)

        self.worker = WorkerThread(file_path, self.parse_checkbox.isChecked(),
                                   self.word_count_checkbox.isChecked(), min_count, max_count)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_finished(self, message):
        self.progress.setRange(0, 1)
        self.progress.setValue(1)
        self.statusBar().showMessage('Ready')
        self.process_button.setEnabled(True)
        QMessageBox.information(self, "Success", message)

    def on_error(self, error_message):
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.statusBar().showMessage('Ready')
        self.process_button.setEnabled(True)
        QMessageBox.warning(self, "Error", error_message)

def main():
    app = QApplication(sys.argv)
    ex = DocxParserGUI()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()