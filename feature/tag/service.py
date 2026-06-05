from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.novel import Tag


DEFAULT_TAGS = [
    {"name": "Fantasy", "description": "Magic, secondary worlds, mythical beings, or fantastical events."},
    {"name": "High Fantasy", "description": "Epic fantasy set mainly in a fully fictional world."},
    {"name": "Low Fantasy", "description": "Fantasy where magical elements intrude into a familiar world."},
    {"name": "Dark Fantasy", "description": "Fantasy with horror, bleak tone, or morally harsh settings."},
    {"name": "Urban Fantasy", "description": "Fantasy set in modern cities or contemporary society."},
    {"name": "Historical Fantasy", "description": "Historical settings mixed with magic or fantasy elements."},
    {"name": "Science Fantasy", "description": "A blend of science fiction concepts and fantasy elements."},
    {"name": "Sword and Sorcery", "description": "Personal-stakes fantasy with warriors, magic, and adventure."},
    {"name": "Mythology", "description": "Stories drawing on gods, legends, folklore, or mythic figures."},
    {"name": "Supernatural", "description": "Ghosts, spirits, curses, demons, or paranormal forces."},
    {"name": "Horror", "description": "Stories built around fear, dread, monsters, or disturbing events."},
    {"name": "Mystery", "description": "Stories driven by secrets, puzzles, or unknown events."},
    {"name": "Detective", "description": "Investigators solving crimes, puzzles, or hidden truths."},
    {"name": "Crime", "description": "Criminal activity, gangs, law enforcement, or underworld plots."},
    {"name": "Thriller", "description": "Suspenseful stories driven by danger, tension, and urgency."},
    {"name": "Psychological", "description": "Mental pressure, manipulation, trauma, or inner conflict."},
    {"name": "Action", "description": "Fast-paced conflict, fights, chases, and danger."},
    {"name": "Adventure", "description": "Journeys, quests, exploration, and discovery."},
    {"name": "War", "description": "Stories centered on armed conflict and its consequences."},
    {"name": "Military Fiction", "description": "Stories focused on soldiers, campaigns, tactics, or command."},
    {"name": "Survival", "description": "Characters struggling to endure hostile conditions."},
    {"name": "Romance", "description": "Stories focused on romantic relationships."},
    {"name": "Contemporary Romance", "description": "Romance set in modern everyday society."},
    {"name": "Historical Romance", "description": "Romance set in a historical period."},
    {"name": "Drama", "description": "Character conflict, emotion, and serious personal stakes."},
    {"name": "Comedy", "description": "Humor-driven stories and lighter conflicts."},
    {"name": "Tragedy", "description": "Loss, downfall, sacrifice, or painful consequences."},
    {"name": "Slice of Life", "description": "Everyday life, routines, relationships, and small moments."},
    {"name": "Coming of Age", "description": "Growth, maturity, identity, and formative experiences."},
    {"name": "School Life", "description": "Stories centered on school, academy, or student life."},
    {"name": "Historical", "description": "Stories set in real or inspired historical periods."},
    {"name": "Alternate History", "description": "Stories exploring changed versions of historical events."},
    {"name": "Science Fiction", "description": "Fiction centered on science, technology, or future society."},
    {"name": "Space Opera", "description": "Large-scale science fiction across planets, empires, or space wars."},
    {"name": "Cyberpunk", "description": "High tech, low life, corporate control, and digital society."},
    {"name": "Steampunk", "description": "Retro-futuristic fiction with steam-era technology."},
    {"name": "Post-Apocalyptic", "description": "Life after collapse, disaster, plague, or world-ending events."},
    {"name": "Dystopian", "description": "Oppressive societies, control systems, and resistance."},
    {"name": "Time Travel", "description": "Movement across time, timelines, loops, or altered history."},
    {"name": "LitRPG", "description": "Game-like systems, stats, classes, levels, or quests."},
    {"name": "Isekai", "description": "Characters transported, summoned, or reborn into another world."},
    {"name": "Reincarnation", "description": "A character is reborn with a new life, body, or identity."},
    {"name": "Transmigration", "description": "A character moves into another world, body, timeline, or story."},
    {"name": "Progression Fantasy", "description": "Power growth, training, ranks, and long-term advancement."},
    {"name": "Cultivation", "description": "Spiritual advancement, realms, techniques, and sects."},
    {"name": "Martial Arts", "description": "Combat training, tournaments, techniques, and fighters."},
    {"name": "Mecha", "description": "Stories centered on giant robots, pilots, machines, or mechanical warfare."},
]

OBSOLETE_DEFAULT_TAGS = ["Warhammer"]


async def seed_default_tags(db: AsyncSession) -> int:
    obsolete_names_lower = [name.lower() for name in OBSOLETE_DEFAULT_TAGS]
    obsolete_result = await db.execute(
        select(Tag).where(func.lower(Tag.tag_name).in_(obsolete_names_lower))
    )
    for tag in obsolete_result.scalars().all():
        tag.tag_isactive = False

    tag_names_lower = [tag["name"].lower() for tag in DEFAULT_TAGS]
    result = await db.execute(
        select(Tag.tag_name).where(func.lower(Tag.tag_name).in_(tag_names_lower))
    )
    existing_names = {name.lower() for name in result.scalars().all()}

    new_tags = [
        Tag(
            tag_name=tag["name"],
            tag_description=tag["description"],
            tag_isactive=True,
        )
        for tag in DEFAULT_TAGS
        if tag["name"].lower() not in existing_names
    ]

    if not new_tags:
        return 0

    db.add_all(new_tags)
    await db.commit()
    return len(new_tags)

