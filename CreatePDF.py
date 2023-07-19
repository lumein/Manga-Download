import os
from pathlib import Path
from PIL import Image
from PyPDF2 import PdfMerger, PdfReader
from tkinter import Tk, filedialog, simpledialog

def get_pdf_files(folder):
    """Get a list of PDF files in a folder sorted by chapter number"""
    pdf_files = []
    for chapter_folder in sorted(os.listdir(folder), key=lambda x: int(x)):
        chapter_folder_path = folder / chapter_folder
        if chapter_folder_path.is_dir():
            images = []
            for image_file in os.listdir(chapter_folder_path):
                if not image_file.startswith(".") and image_file.lower().endswith((".png", ".jpg", ".jpeg")):
                    image = Image.open(chapter_folder_path / image_file)
                    image = image.convert("RGB")
                    images.append(image)
            if images:
                pdf_file = chapter_folder_path.with_suffix(".pdf")
                images[0].save(pdf_file, save_all=True, append_images=images[1:])
                pdf_files.append(pdf_file)
    return pdf_files

def merge_pdf_files(pdf_files, output_file):
    """Merge a list of PDF files into a single PDF file"""
    merger = PdfMerger()
    current_page = 0
    for pdf_file in pdf_files:
        merger.append(str(pdf_file))
        num_pages = len(PdfReader(str(pdf_file)).pages)
        merger.add_outline_item(f"Chapter {pdf_file.stem}", current_page)
        current_page += num_pages
    merger.write(str(output_file))

# Create a Tkinter root window (it will not be shown)
root = Tk()
root.withdraw()

# Open a file chooser dialog to select the path
sd_folder = Path(filedialog.askdirectory(title="Select folder"))

# Get a list of PDF files in the folder sorted by chapter number
pdf_files = get_pdf_files(sd_folder)

# Prompt the user to enter the name of the final PDF file
pdf_name = simpledialog.askstring("PDF Name", "Enter the name of the final PDF file:", initialvalue="One Piece")

# Merge the PDF files into a single PDF file
merge_pdf_files(pdf_files, sd_folder / f"{pdf_name}.pdf")
