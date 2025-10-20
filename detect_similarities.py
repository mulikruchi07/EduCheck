import os
import PyPDF2  # <-- CHANGED
import docx
from pathlib import Path

def read_txt(file_path):
    """Reads text from a .txt file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""

def read_pdf(file_path):
    """Reads text from a .pdf file using PyPDF2 (low memory)."""
    text = ""
    try:
        # PyPDF2 needs the file to be opened in binary mode
        with open(file_path, 'rb') as f: 
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        # Catch PyPDF2 specific errors
        if "Bad CRC-32" in str(e):
            print(f"Skipping corrupted file: {file_path.name}")
        else:
            print(f"Error reading {file_path}: {e}")
        return ""

def read_docx(file_path):
    """Reads text from a .docx file."""
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        # This will catch the 'Bad CRC-32' errors for docx
        print(f"Error reading {file_path}: {e}")
        return ""

def collect_documents(directory):
    """
    Walks through a directory, reads supported files, and returns file paths and their content.
    """
    paths = []
    docs = []
    
    # Supported file extensions and their reader functions
    SUPPORTED_EXTENSIONS = {
        ".txt": read_txt,
        ".pdf": read_pdf,
        ".docx": read_docx,
    }

    print(f"--- Collecting documents from: {directory} ---")

    for root, _, files in os.walk(directory):
        for file in files:
            file_path = Path(os.path.join(root, file))
            file_ext = file_path.suffix.lower()

            if file_ext in SUPPORTED_EXTENSIONS:
                print(f"Reading: {file_path.name}")
                # Get the appropriate reader function for the extension
                reader = SUPPORTED_EXTENSIONS[file_ext]
                content = reader(file_path)
                
                if content:
                    paths.append(file_path)
                    docs.append(content)
            else:
                print(f"Skipping unsupported file: {file_path.name}")

    print(f"--- Collected {len(docs)} documents. ---")
    return paths, docs