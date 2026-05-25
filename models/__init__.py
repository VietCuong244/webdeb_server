from database import Base

from .user import User
from .novel import Novel, Tag, NoveltoTags
from .report import Report
from .document import Document, Embedding