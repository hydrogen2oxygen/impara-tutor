from typing import Optional

from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    display_name: Mapped[str]
    email: Mapped[Optional[str]]
    bio: Mapped[Optional[str]]
    avatar_path: Mapped[Optional[str]]
    created_at: Mapped[str]
    last_active_at: Mapped[Optional[str]]

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, display_name={self.display_name!r}, email={self.email!r}, bio={self.bio!r}, avatar_path={self.avatar_path!r})"

class Language(Base):
    __tablename__ = "language"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    source_language: Mapped[str]
    target_language: Mapped[str]
    created_at: Mapped[str]

    def __repr__(self) -> str:
        return f"Language(id={self.id!r}, user_id={self.user_id!r}, source_language={self.source_language!r}, target_language={self.target_language!r})"
    
class Languages(Base):
    __tablename__ = "languages"
    __table_args__ = (
        UniqueConstraint("code", "name", name="uq_languages_code_name"),
    )

    code: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]

    def __repr__(self) -> str:
        return f"Languages(code={self.code!r}, name={self.name!r})"