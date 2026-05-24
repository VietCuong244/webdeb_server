import fitz as PDF
import pymupdf4llm
import os

def pdf_to_data(pdf_name):
    
    pdf_path = f"local_storage/pdf/{pdf_name}"
    pdf_base_name = os.path.splitext(pdf_name)[0]
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"The file {pdf_name} does not exist.")
    
    try:
        image_dir = f"local_storage/image/{pdf_base_name}"
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
    
def save_markdown(md_text, pdf_name):

    md_filename = f"local_storage/markdown/{os.path.splitext(pdf_name)[0]}.md"
    try:
        with open(md_filename, "w", encoding="utf-8") as md_file:
            md_file.write(md_text)
        return md_filename
    except Exception as e:
        raise RuntimeError(f"An error occurred while saving the markdown file: {e}")
