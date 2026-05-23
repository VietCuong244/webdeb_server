from feature.auth.router import router_auth
from feature.user.router import router_user
from feature.tag.router import router_tag
from feature.tag.service import seed_default_tags
import models
from database import SessionLocal, engine, Base
from sqlalchemy import text
from fastapi import FastAPI,  Depends 

app = FastAPI()
app.include_router(router_auth)
app.include_router(router_user)
app.include_router(router_tag)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("""
            ALTER TABLE documents
            ADD COLUMN IF NOT EXISTS doc_fts tsvector
            GENERATED ALWAYS AS (
                setweight(to_tsvector('simple', coalesce(doc_title, '')), 'A') ||
                setweight(to_tsvector('simple', coalesce(doc_content, '')), 'B')
            ) STORED
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_documents_doc_fts
            ON documents
            USING gin (doc_fts)
        """))

    async with SessionLocal() as db:
        await seed_default_tags(db)
        

@app.get("/")
async def root():
    return {"message": "Hello World"}
