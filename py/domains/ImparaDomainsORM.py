from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy import Index
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


class Course(Base):
    __tablename__ = "course"
    __table_args__ = (
        UniqueConstraint("target_language", "title", name="uq_course_target_language_title"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    target_language: Mapped[str]
    title: Mapped[str]
    description: Mapped[Optional[str]]
    source_link: Mapped[Optional[str]]
    tags: Mapped[Optional[str]]
    created_at: Mapped[str]

    def __repr__(self) -> str:
        return f"Course(id={self.id!r}, user_id={self.user_id!r}, target_language={self.target_language!r}, title={self.title!r})"


class Lesson(Base):
    __tablename__ = "lesson"
    __table_args__ = (
        UniqueConstraint("course_id", "title", name="uq_lesson_course_id_title"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id"))
    parent_lesson_id: Mapped[Optional[int]] = mapped_column(ForeignKey("lesson.id"))
    title: Mapped[str]
    description: Mapped[Optional[str]]
    text: Mapped[Optional[str]]
    source_link: Mapped[Optional[str]]
    tags: Mapped[Optional[str]]
    created_at: Mapped[str]

    def __repr__(self) -> str:
        return f"Lesson(id={self.id!r}, user_id={self.user_id!r}, course_id={self.course_id!r}, title={self.title!r})"


class DictEntry(Base):
    __tablename__ = "dict_entry"
    __table_args__ = (
        UniqueConstraint("language", "lemma", name="uq_dict_entry_language_lemma"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    language: Mapped[str]
    lemma: Mapped[str]
    normalized: Mapped[Optional[str]]
    ipa: Mapped[Optional[str]]
    created_at: Mapped[str]

    def __repr__(self) -> str:
        return f"DictEntry(id={self.id!r}, language={self.language!r}, lemma={self.lemma!r})"


class DictSense(Base):
    __tablename__ = "dict_sense"
    __table_args__ = (
        UniqueConstraint("entry_id", "sense_order", name="uq_dict_sense_entry_id_sense_order"),
        Index("idx_sense_entry", "entry_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    entry_id: Mapped[int] = mapped_column(ForeignKey("dict_entry.id", ondelete="CASCADE"))
    pos: Mapped[Optional[str]]
    gloss: Mapped[Optional[str]]
    note: Mapped[Optional[str]]
    sense_order: Mapped[Optional[int]]

    def __repr__(self) -> str:
        return f"DictSense(id={self.id!r}, entry_id={self.entry_id!r}, pos={self.pos!r})"


class DictTranslation(Base):
    __tablename__ = "dict_translation"
    __table_args__ = (
        UniqueConstraint("sense_id", "target_language", "translation", name="uq_dict_translation_sense_id_target_language_translation"),
        Index("idx_tr_sense", "sense_id"),
        Index("idx_tr_lang", "target_language", "translation"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sense_id: Mapped[int] = mapped_column(ForeignKey("dict_sense.id", ondelete="CASCADE"))
    target_language: Mapped[str]
    translation: Mapped[str]
    note: Mapped[Optional[str]]

    def __repr__(self) -> str:
        return f"DictTranslation(id={self.id!r}, sense_id={self.sense_id!r}, target_language={self.target_language!r}, translation={self.translation!r})"


class DictExample(Base):
    __tablename__ = "dict_example"
    __table_args__ = (
        Index("idx_ex_sense", "sense_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sense_id: Mapped[int] = mapped_column(ForeignKey("dict_sense.id", ondelete="CASCADE"))
    example: Mapped[str]
    translation: Mapped[Optional[str]]
    source: Mapped[Optional[str]]

    def __repr__(self) -> str:
        return f"DictExample(id={self.id!r}, sense_id={self.sense_id!r}, example={self.example!r})"


class UserSenseState(Base):
    __tablename__ = "user_sense_state"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    sense_id: Mapped[int] = mapped_column(ForeignKey("dict_sense.id", ondelete="CASCADE"), primary_key=True)
    srs_level: Mapped[int]
    last_seen_at: Mapped[Optional[str]]
    next_due_at: Mapped[Optional[str]]

    def __repr__(self) -> str:
        return f"UserSenseState(user_id={self.user_id!r}, sense_id={self.sense_id!r}, srs_level={self.srs_level!r})"