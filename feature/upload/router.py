from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from feature.user.service import require_unlocked_user
from database import get_db
from models.document import Document
from models.novel import Novel
import os
from .pdfprocessor import pdf_to_data, save_markdown
from .schema import PDFUploadRequest

router_upload = APIRouter(prefix="/upload", tags=["upload"])
pdf_storage_path = "local_storage/pdf/"
markdown_storage_path = "local_storage/markdown/"
image_storage_path = "local_storage/image/"
cover_storage_path = "local_storage/cover/"

@router_upload.post("/pdf")
async def upload_pdf(
    data: PDFUploadRequest = Depends(PDFUploadRequest.as_form),
    pdf_file: UploadFile = File(...),
    cover_file: UploadFile = File(...),
    current_user = Depends(require_unlocked_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        if pdf_file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        os.makedirs(pdf_storage_path, exist_ok=True)
        os.makedirs(markdown_storage_path, exist_ok=True)
        os.makedirs(image_storage_path, exist_ok=True)
        os.makedirs(cover_storage_path, exist_ok=True)
        
        pdf_name = pdf_file.filename
        pdf_path = os.path.join(pdf_storage_path, pdf_name)
        with open(pdf_path, "wb") as f:
            f.write(await pdf_file.read())

        cover_path = os.path.join(cover_storage_path, cover_file.filename)
        with open(cover_path, "wb") as f:
            f.write(await cover_file.read())

        md_text = pdf_to_data(pdf_name)
        markdown_path = save_markdown(md_text, pdf_name)

        new_novel = Novel(
            novel_title=data.novel_title,
            novel_author=data.novel_author,
            novel_user=current_user.user_id,
            novel_descriptionurl=data.novel_descriptionurl,
            novel_coverurl=cover_path,
            novel_series=data.novel_series,
            novel_isprivate=data.novel_isprivate,
        )
        db.add(new_novel)
        await db.flush()

        new_doc = Document(
            doc_novel_id=new_novel.novel_id,
            doc_title=data.novel_title,
            doc_source=data.doc_source,
            doc_fileurl=pdf_path,
            doc_markdownurl=markdown_path,
        )
        db.add(new_doc)
        await db.commit()
        await db.refresh(new_doc)

        return {
            "message": "PDF uploaded and processed successfully",
            "novel_id": new_novel.novel_id,
            "novel_title": new_novel.novel_title,
            "novel_coverurl": new_novel.novel_coverurl,
            "document_id": new_doc.doc_id,
            "doc_title": new_doc.doc_title,
            "doc_fileurl": new_doc.doc_fileurl,
            "doc_markdownurl": new_doc.doc_markdownurl,
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
