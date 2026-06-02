import fitz as PDF
import pymupdf4llm
import os
import uuid
from uuid import UUID

from fastapi import HTTPException, UploadFile
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import SessionLocal
from models.document import Document
from models.novel import Novel, NoveltoTags, Tag


PDF_STORAGE_PATH = "local_storage/pdf/"
MARKDOWN_STORAGE_PATH = "local_storage/markdown/"
IMAGE_STORAGE_PATH = "local_storage/image/"
COVER_STORAGE_PATH = "local_storage/cover/"


def ensure_storage_dirs():
    os.makedirs(PDF_STORAGE_PATH, exist_ok=True)
    os.makedirs(MARKDOWN_STORAGE_PATH, exist_ok=True)
    os.makedirs(IMAGE_STORAGE_PATH, exist_ok=True)
    os.makedirs(COVER_STORAGE_PATH, exist_ok=True)

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


async def save_upload_files(pdf_file: UploadFile, cover_file: UploadFile):
    if pdf_file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    ensure_storage_dirs()

    upload_id = uuid.uuid4().hex
    pdf_ext = os.path.splitext(pdf_file.filename or "")[1].lower() or ".pdf"
    cover_ext = os.path.splitext(cover_file.filename or "")[1].lower()

    pdf_name = f"{upload_id}{pdf_ext}"
    pdf_path = os.path.join(PDF_STORAGE_PATH, pdf_name)
    with open(pdf_path, "wb") as f:
        f.write(await pdf_file.read())

    cover_name = f"{upload_id}{cover_ext}" if cover_ext else f"{upload_id}_cover"
    cover_path = os.path.join(COVER_STORAGE_PATH, cover_name)
    with open(cover_path, "wb") as f:
        f.write(await cover_file.read())

    return {
        "upload_id": upload_id,
        "pdf_path": pdf_path,
        "cover_path": cover_path,
        "image_dir": os.path.join(IMAGE_STORAGE_PATH, upload_id),
        "markdown_path": os.path.join(MARKDOWN_STORAGE_PATH, f"{upload_id}.md"),
    }


async def save_pdf_file(pdf_file: UploadFile):
    if pdf_file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    ensure_storage_dirs()

    upload_id = uuid.uuid4().hex
    pdf_ext = os.path.splitext(pdf_file.filename or "")[1].lower() or ".pdf"

    pdf_name = f"{upload_id}{pdf_ext}"
    pdf_path = os.path.join(PDF_STORAGE_PATH, pdf_name)
    with open(pdf_path, "wb") as f:
        f.write(await pdf_file.read())

    return {
        "upload_id": upload_id,
        "pdf_path": pdf_path,
        "image_dir": os.path.join(IMAGE_STORAGE_PATH, upload_id),
        "markdown_path": os.path.join(MARKDOWN_STORAGE_PATH, f"{upload_id}.md"),
    }


async def save_cover_file(cover_file: UploadFile, file_stem: str):
    ensure_storage_dirs()

    cover_ext = os.path.splitext(cover_file.filename or "")[1].lower()
    cover_name = f"{file_stem}{cover_ext}" if cover_ext else f"{file_stem}_cover"
    cover_path = os.path.join(COVER_STORAGE_PATH, cover_name)
    with open(cover_path, "wb") as f:
        f.write(await cover_file.read())

    return cover_path


async def replace_novel_tags(db: AsyncSession, novel_id: UUID, tag_ids: list[UUID]):
    unique_tag_ids = list(dict.fromkeys(tag_ids))

    await db.execute(delete(NoveltoTags).where(NoveltoTags.novel_id == novel_id))

    if not unique_tag_ids:
        return []

    result = await db.execute(select(Tag).where(Tag.tag_id.in_(unique_tag_ids)))
    tags = result.scalars().all()
    found_tag_ids = {tag.tag_id for tag in tags}
    missing_tag_ids = [str(tag_id) for tag_id in unique_tag_ids if tag_id not in found_tag_ids]
    if missing_tag_ids:
        raise HTTPException(status_code=400, detail=f"Tag not found: {', '.join(missing_tag_ids)}")

    db.add_all([
        NoveltoTags(novel_id=novel_id, tag_id=tag_id)
        for tag_id in unique_tag_ids
    ])
    return tags


async def create_upload_records(db: AsyncSession, data, current_user, paths: dict):
    new_novel = Novel(
        novel_title=data.novel_title,
        novel_author=data.novel_author,
        novel_user=current_user.user_id,
        novel_description=data.novel_description,
        novel_coverurl=paths["cover_path"],
        novel_series=data.novel_series,
        novel_isprivate=data.novel_isprivate,
    )
    db.add(new_novel)
    await db.flush()

    new_doc = Document(
        doc_novel_id=new_novel.novel_id,
        doc_title=data.novel_title,
        doc_source=data.doc_source,
        doc_fileurl=paths["pdf_path"],
        doc_markdownurl=paths["markdown_path"],
        doc_status="pending",
    )
    db.add(new_doc)
    await replace_novel_tags(db, new_novel.novel_id, data.tag_ids)
    await db.commit()
    await db.refresh(new_doc)

    return new_novel, new_doc


async def create_pending_upload_records(db: AsyncSession, current_user, paths: dict):
    new_novel = Novel(
        novel_title="Untitled",
        novel_author="Unknown",
        novel_user=current_user.user_id,
        novel_isprivate=True,
    )
    db.add(new_novel)
    await db.flush()

    new_doc = Document(
        doc_novel_id=new_novel.novel_id,
        doc_title="Untitled",
        doc_source="upload",
        doc_fileurl=paths["pdf_path"],
        doc_markdownurl=paths["markdown_path"],
        doc_status="pending",
    )
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)

    return new_novel, new_doc


async def update_upload_information(db: AsyncSession, document: Document, novel: Novel, data, cover_file: UploadFile):
    if document.doc_status != "completed":
        raise HTTPException(status_code=400, detail="Document processing is not completed")

    cover_path = await save_cover_file(cover_file, str(document.doc_id))

    novel.novel_title = data.novel_title
    novel.novel_author = data.novel_author
    novel.novel_description = data.novel_description
    novel.novel_coverurl = cover_path
    novel.novel_series = data.novel_series
    novel.novel_isprivate = data.novel_isprivate
    document.doc_title = data.novel_title

    tags = await replace_novel_tags(db, novel.novel_id, data.tag_ids)

    await db.commit()
    await db.refresh(novel)
    await db.refresh(document)

    return novel, document, tags


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
