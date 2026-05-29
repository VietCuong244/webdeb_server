from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from feature.user.service import require_unlocked_user
from database import SessionLocal, get_db
from models.document import Document
from models.novel import Novel
import os
import uuid
from .pdfprocessor import pdf_to_data, save_markdown
from .schema import PDFUploadRequest

router_upload = APIRouter(prefix="/upload", tags=["upload"])
pdf_storage_path = "local_storage/pdf/"
markdown_storage_path = "local_storage/markdown/"
image_storage_path = "local_storage/image/"
cover_storage_path = "local_storage/cover/"


async def process_pdf_background(document_id, pdf_path: str, markdown_path: str, image_dir: str):
    async with SessionLocal() as db:
        document = await db.get(Document, document_id)
        if not document:
            return

        try:
            document.doc_status = "processing"
            document.doc_error = None
            await db.commit()

            md_text = pdf_to_data(pdf_path, image_dir)
            document.doc_markdownurl = save_markdown(md_text, markdown_path)
            document.doc_status = "completed"
            await db.commit()
        except Exception as e:
            document.doc_status = "failed"
            document.doc_error = str(e)
            await db.commit()


@router_upload.post("/pdf")
async def upload_pdf(
    background_tasks: BackgroundTasks,
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
        
        upload_id = uuid.uuid4().hex
        pdf_ext = os.path.splitext(pdf_file.filename or "")[1].lower() or ".pdf"
        cover_ext = os.path.splitext(cover_file.filename or "")[1].lower()

        pdf_name = f"{upload_id}{pdf_ext}"
        pdf_path = os.path.join(pdf_storage_path, pdf_name)
        with open(pdf_path, "wb") as f:
            f.write(await pdf_file.read())

        cover_name = f"{upload_id}{cover_ext}" if cover_ext else f"{upload_id}_cover"
        cover_path = os.path.join(cover_storage_path, cover_name)
        with open(cover_path, "wb") as f:
            f.write(await cover_file.read())

        image_dir = os.path.join(image_storage_path, upload_id)
        markdown_path = os.path.join(markdown_storage_path, f"{upload_id}.md")

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
            doc_status="pending",
        )
        db.add(new_doc)
        await db.commit()
        await db.refresh(new_doc)

        background_tasks.add_task(
            process_pdf_background,
            new_doc.doc_id,
            pdf_path,
            markdown_path,
            image_dir,
        )

        return {
            "message": "PDF uploaded successfully. Processing started.",
            "status": new_doc.doc_status,
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


@router_upload.get("/documents/{document_id}/status")
async def get_document_status(document_id: str, current_user = Depends(require_unlocked_user), db: AsyncSession = Depends(get_db)):
    document = await db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "document_id": document.doc_id,
        "status": document.doc_status,
        "error": document.doc_error,
        "markdown_url": document.doc_markdownurl if document.doc_status == "completed" else None,
    }
