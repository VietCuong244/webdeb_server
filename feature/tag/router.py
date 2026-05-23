from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from feature.user.service import require_admin
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from models.novel import Tag
from models.user import User
from .schema import TagBase



router_tag = APIRouter(prefix="/tag", tags=["tag"])



@router_tag.post("/create_tag")
async def create_tag(tag: TagBase, current_user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    existing_tag = (
        await db.execute(select(Tag).where(func.lower(Tag.tag_name) == tag.name.lower()))
    ).scalar_one_or_none()
    if existing_tag:
        raise HTTPException(status_code=400, detail="Tag already exists")

    new_tag = Tag(
        tag_name=tag.name,
        tag_description=tag.description,
        tag_isactive=tag.is_active,
    )
    db.add(new_tag)
    await db.commit()
    await db.refresh(new_tag)
    return {
        "message": "Tag created successfully",
        "tag": {
            "tag_id": new_tag.tag_id,
            "tag_name": new_tag.tag_name,
            "tag_description": new_tag.tag_description,
            "tag_isactive": new_tag.tag_isactive,
        },
    }

@router_tag.get("/list_tags")
async def list_tags(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag).order_by(Tag.tag_name))
    tags = result.scalars().all()
    return {
        "tags": [
            {
                "tag_id": tag.tag_id,
                "tag_name": tag.tag_name,
                "tag_description": tag.tag_description,
                "tag_isactive": tag.tag_isactive,
            }
            for tag in tags
        ]
    }
