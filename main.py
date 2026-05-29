from feature.auth.router import router_auth
from feature.user.router import router_user
from feature.tag.router import router_tag
from feature.novel.router import router_novel
from feature.upload.router import router_upload

from feature.tag.service import seed_default_tags
import models
from database import SessionLocal, engine, Base
from sqlalchemy import text
from fastapi import FastAPI,  Depends 

app = FastAPI()
app.include_router(router_auth)
app.include_router(router_user)
app.include_router(router_tag)
app.include_router(router_upload)
app.include_router(router_novel)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("""
            ALTER TABLE documents
            ADD COLUMN IF NOT EXISTS doc_fileurl varchar
        """))
        await conn.execute(text("""
            ALTER TABLE documents
            ADD COLUMN IF NOT EXISTS doc_markdownurl varchar
        """))
        await conn.execute(text("""
            ALTER TABLE documents
            ADD COLUMN IF NOT EXISTS doc_novel_id uuid
        """))
        await conn.execute(text("""
            ALTER TABLE documents
            ADD COLUMN IF NOT EXISTS doc_status varchar NOT NULL DEFAULT 'pending'
        """))
        await conn.execute(text("""
            ALTER TABLE documents
            ADD COLUMN IF NOT EXISTS doc_error text
        """))
        await conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1
                    FROM information_schema.key_column_usage kcu
                    JOIN information_schema.table_constraints tc
                      ON tc.constraint_name = kcu.constraint_name
                     AND tc.table_schema = kcu.table_schema
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                      AND kcu.table_name = 'documents'
                      AND kcu.column_name = 'doc_novel_id'
                ) THEN
                    ALTER TABLE documents
                    ADD CONSTRAINT fk_documents_doc_novel_id
                    FOREIGN KEY (doc_novel_id) REFERENCES novels(novel_id)
                    ON DELETE CASCADE;
                END IF;
            END $$;
        """))
        await conn.execute(text("""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = 'documents'
                      AND column_name = 'doc_content'
                ) THEN
                    ALTER TABLE documents ALTER COLUMN doc_content DROP NOT NULL;
                END IF;
            END $$;
        """))
        await conn.execute(text("""
            ALTER TABLE embeddings
            ADD COLUMN IF NOT EXISTS emb_fts tsvector
            GENERATED ALWAYS AS (
                to_tsvector('simple', coalesce(emb_chunk, ''))
            ) STORED
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_embeddings_emb_fts
            ON embeddings
            USING gin (emb_fts)
        """))

    async with SessionLocal() as db:
        await seed_default_tags(db)
        

@app.get("/")
async def root():
    return {"message": "Hello World"}
