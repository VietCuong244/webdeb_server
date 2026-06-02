from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from feature.user.service import require_unlocked_user
from database import get_db
from models.document import Document
from models.novel import Novel
from uuid import UUID
from .service import (
    create_pending_upload_records,
    create_upload_records,
    process_pdf_background,
    save_pdf_file,
    save_upload_files,
    update_upload_information,
)
from .schema import PDFUploadRequest

router_upload = APIRouter(prefix="/upload", tags=["upload"])


@router_upload.post("/pdf/start")
async def start_pdf_upload(
    background_tasks: BackgroundTasks,
    pdf_file: UploadFile = File(...),
    current_user = Depends(require_unlocked_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        paths = await save_pdf_file(pdf_file)
        new_novel, new_doc = await create_pending_upload_records(db, current_user, paths)

        background_tasks.add_task(
            process_pdf_background,
            new_doc.doc_id,
            paths["pdf_path"],
            paths["markdown_path"],
            paths["image_dir"],
        )

        return {
            "message": "PDF uploaded. Processing started.",
            "status": new_doc.doc_status,
            "novel_id": new_novel.novel_id,
            "document_id": new_doc.doc_id,
            "doc_fileurl": new_doc.doc_fileurl,
            "doc_markdownurl": new_doc.doc_markdownurl,
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        paths = await save_upload_files(pdf_file, cover_file)
        new_novel, new_doc = await create_upload_records(db, data, current_user, paths)

        background_tasks.add_task(
            process_pdf_background,
            new_doc.doc_id,
            paths["pdf_path"],
            paths["markdown_path"],
            paths["image_dir"],
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
            "tag_ids": data.tag_ids,
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router_upload.get("/documents/{document_id}/status")
async def get_document_status(document_id: UUID, current_user = Depends(require_unlocked_user), db: AsyncSession = Depends(get_db)):
    document = await db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    novel = await db.get(Novel, document.doc_novel_id)
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")  
    if current_user.user_role != "admin" and current_user.user_id != novel.novel_user: 
        raise HTTPException(status_code=403, detail="Access denied")
    return {
        "document_id": document.doc_id,
        "status": document.doc_status,
        "error": document.doc_error,
        "markdown_url": document.doc_markdownurl if document.doc_status == "completed" else None,
        "can_update_information": document.doc_status == "completed",
    }


@router_upload.put("/documents/{document_id}/information")
async def update_document_information(
    document_id: UUID,
    data: PDFUploadRequest = Depends(PDFUploadRequest.as_form),
    cover_file: UploadFile = File(...),
    current_user = Depends(require_unlocked_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        document = await db.get(Document, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        novel = await db.get(Novel, document.doc_novel_id)
        if not novel:
            raise HTTPException(status_code=404, detail="Novel not found")

        if current_user.user_role != "admin" and current_user.user_id != novel.novel_user:
            raise HTTPException(status_code=403, detail="Access denied")

        novel, document, tags = await update_upload_information(
            db,
            document,
            novel,
            data,
            cover_file,
        )

        return {
            "message": "Novel information updated successfully",
            "novel_id": novel.novel_id,
            "novel_title": novel.novel_title,
            "novel_author": novel.novel_author,
            "novel_description": novel.novel_description,
            "novel_coverurl": novel.novel_coverurl,
            "novel_series": novel.novel_series,
            "novel_isprivate": novel.novel_isprivate,
            "document_id": document.doc_id,
            "doc_title": document.doc_title,
            "tags": [
                {
                    "tag_id": tag.tag_id,
                    "tag_name": tag.tag_name,
                }
                for tag in tags
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
