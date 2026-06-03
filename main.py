from feature.auth.router import router_auth
from feature.user.router import router_user
from feature.tag.router import router_tag
from feature.novel.router import router_novel
from feature.upload.router import router_upload
from feature.admin.router import router_admin
from feature.report.router import router_report

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
app.include_router(router_admin)
app.include_router(router_report)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with SessionLocal() as db:
        await seed_default_tags(db)
        

@app.get("/")
async def root():
    return {"message": "PDF web"}


