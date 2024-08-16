import os
os.environ['TK_SILENCE_DEPRECATION'] = '1'  # Silence Tk deprecation warning

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from docx_parser_functions import parse_docx, create_word_count_summary, create_output_folder, list_docx_files

class DocxParserGUI:
    def __init__(self, master):
        self.master = master
        master.title("DOCX Parser")
        master.geometry("600x400")

        self.file_path = tk.StringVar()
        self.parse_var = tk.BooleanVar(value=True)
        self.word_count_var = tk.BooleanVar()
        self.min_count = tk.StringVar(value="5")
        self.max_count = tk.StringVar(value="80")
        self.status_var = tk.StringVar(value="Ready")

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        ttk.Label(main_frame, text="Select DOCX file:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(main_frame, textvariable=self.file_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=5, pady=5)

        ttk.Checkbutton(main_frame, text="Parse document", variable=self.parse_var).grid(row=1, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)
        ttk.Checkbutton(main_frame, text="Create word count summary", variable=self.word_count_var).grid(row=2, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)

        ttk.Label(main_frame, text="Min word count:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(main_frame, textvariable=self.min_count, width=5).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(main_frame, text="Max word count:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(main_frame, textvariable=self.max_count, width=5).grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Button(main_frame, text="Process", command=self.process_threaded).grid(row=5, column=0, padx=5, pady=5)
        ttk.Button(main_frame, text="Exit", command=self.master.quit).grid(row=5, column=1, padx=5, pady=5)

        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=200, mode='indeterminate')
        self.progress.grid(row=6, column=0, columnspan=3, padx=5, pady=5, sticky=(tk.W, tk.E))

        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E))

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("DOCX Files", "*.docx")])
        self.file_path.set(filename)

    def process_threaded(self):
        threading.Thread(target=self.process, daemon=True).start()

    def process(self):
        self.progress.start()
        self.status_var.set("Processing...")
        file_path = self.file_path.get()
        if not file_path:
            self.show_error("Please select a DOCX file.")
            self.progress.stop()
            self.status_var.set("Ready")
            return

        try:
            output_folder = create_output_folder()

            if self.parse_var.get():
                parsed_content = parse_docx(file_path)
                if parsed_content:
                    self.show_info(f"Document parsed. Output saved in {output_folder}")
                else:
                    self.show_error("No content found in the document.")

            if self.word_count_var.get():
                try:
                    min_count = int(self.min_count.get())
                    max_count = int(self.max_count.get())
                    create_word_count_summary([os.path.basename(file_path)], output_folder, min_count, max_count)
                    self.show_info(f"Word count summary created in {output_folder}")
                except ValueError:
                    self.show_error("Please enter valid numbers for min and max word count.")
        except Exception as e:
            self.show_error(f"An error occurred: {str(e)}")
        finally:
            self.progress.stop()
            self.status_var.set("Ready")

    def show_error(self, message):
        self.status_var.set("Error")
        messagebox.showerror("Error", message)

    def show_info(self, message):
        self.status_var.set("Done")
        messagebox.showinfo("Success", message)

def main():
    root = tk.Tk()
    app = DocxParserGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()