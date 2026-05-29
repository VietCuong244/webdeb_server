import fitz as PDF
import pymupdf4llm
import os

def pdf_to_data(pdf_path: str, image_dir: str):
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"The file {pdf_path} does not exist.")
    
    try:
        os.makedirs(image_dir, exist_ok=True)
        
        with PDF.open(pdf_path) as document:
            md_text = pymupdf4llm.to_markdown(
                doc=document,
                write_images=True,
                image_path=image_dir
            )
        return md_text
    
    except Exception as e:
        raise RuntimeError(f"An error occurred while processing the PDF: {e}")
    
def save_markdown(md_text: str, markdown_path: str):

    try:
        os.makedirs(os.path.dirname(markdown_path), exist_ok=True)
        with open(markdown_path, "w", encoding="utf-8") as md_file:
            md_file.write(md_text)
        return markdown_path
    except Exception as e:
        raise RuntimeError(f"An error occurred while saving the markdown file: {e}")
