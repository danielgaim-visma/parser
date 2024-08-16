import sys
import tkinter as tk
import os

def get_python_info():
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Tkinter version: {tk.TkVersion}")
    print(f"Tcl version: {tk.Tcl().eval('info patchlevel')}")
    print(f"PYTHON_PATH: {os.environ.get('PYTHONPATH', 'Not set')}")
    print(f"DISPLAY: {os.environ.get('DISPLAY', 'Not set')}")
    print("\nPython path:")
    for path in sys.path:
        print(path)

if __name__ == "__main__":
    get_python_info()