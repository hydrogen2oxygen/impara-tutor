import os
from typing import List, Optional
from datetime import datetime
import json

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from py.domains.ImparaDomainsORM import (
    User, Language, Languages, Base,
    Course, Lesson, DictEntry, DictSense, DictTranslation, DictExample, UserSenseState
)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

class ImparaDB:
    def __init__(self, db_filename):
        # Ensure the directory exists before connecting to the database
        db_dir = os.path.dirname(db_filename)
        os.makedirs(db_dir, exist_ok=True)
        self.engine = create_engine(
            f"sqlite:///{db_filename}",
            connect_args={"check_same_thread": False}
        )
        Base.metadata.create_all(self.engine) # <- creates missing tables based on the ORM models
        
        language_list = [
                    # Global major languages
                    ('en', 'English'),
                    ('zh', 'Chinese'),
                    ('hi', 'Hindi'),
                    ('es', 'Spanish'),
                    ('fr', 'French'),
                    ('ar', 'Arabic'),
                    ('bn', 'Bengali'),
                    ('ru', 'Russian'),
                    ('pt', 'Portuguese'),
                    ('ur', 'Urdu'),
                    ('id', 'Indonesian'),
                    ('de', 'German'),
                    ('ja', 'Japanese'),
                    ('sw', 'Swahili'),
                    ('tr', 'Turkish'),
                    ('vi', 'Vietnamese'),
                    ('ko', 'Korean'),
                    ('fa', 'Persian'),
                    ('th', 'Thai'),
                    ('ms', 'Malay'),

                    # European languages
                    ('it', 'Italian'),
                    ('nl', 'Dutch'),
                    ('pl', 'Polish'),
                    ('uk', 'Ukrainian'),
                    ('ro', 'Romanian'),
                    ('cs', 'Czech'),
                    ('el', 'Greek'),
                    ('hu', 'Hungarian'),
                    ('sv', 'Swedish'),
                    ('fi', 'Finnish'),
                    ('da', 'Danish'),
                    ('no', 'Norwegian'),
                    ('sk', 'Slovak'),
                    ('bg', 'Bulgarian'),
                    ('hr', 'Croatian'),
                    ('sr', 'Serbian'),
                    ('sl', 'Slovenian'),
                    ('et', 'Estonian'),
                    ('lv', 'Latvian'),
                    ('lt', 'Lithuanian'),
                    ('ga', 'Irish'),
                    ('mt', 'Maltese'),
                    ('is', 'Icelandic'),
                    ('sq', 'Albanian'),
                    ('mk', 'Macedonian'),
                    ('be', 'Belarusian')
                ]  

        with Session(self.engine) as session:
            for code, name in language_list:
                exists = session.scalar(select(Languages).where(Languages.code == code))
                if not exists:
                    session.add(Languages(code=code, name=name))
            session.commit()

    def close(self):
        self.engine.dispose()

    def insert_user(self, user: User) -> User:
        with Session(self.engine) as session:
            session.add(user)
            session.commit()
            session.refresh(user)  # Refresh to get the generated ID
            return user
        
    def list_users(self) -> List[User]:
        with Session(self.engine) as session:
            return session.query(User).all()
        
    def delete_user(self, user_id: int):
        with Session(self.engine) as session:
            user = session.get(User, user_id)
            if user:
                session.delete(user)
                session.commit()

    def list_languages(self) -> List[Languages]:
        with Session(self.engine) as session:
            return session.query(Languages).all()
        
    def insert_language(self, language: Language) -> Language:
        with Session(self.engine) as session:
            session.add(language)
            session.commit()
            session.refresh(language)  # Refresh to get the generated ID
            return language
        
    def list_user_languages(self, user_id: int) -> List[Language]:
        with Session(self.engine) as session:
            return session.query(Language).filter(Language.user_id == user_id).all()

    # ==================== COURSE CRUD ====================

    def insert_course(self, course: Course) -> Course:
        with Session(self.engine) as session:
            session.add(course)
            session.commit()
            session.refresh(course)
            return course

    def get_course(self, course_id: int) -> Optional[Course]:
        with Session(self.engine) as session:
            return session.get(Course, course_id)

    def update_course(self, course_id: int, **kwargs) -> Optional[Course]:
        with Session(self.engine) as session:
            course = session.get(Course, course_id)
            if course:
                for key, value in kwargs.items():
                    if hasattr(course, key):
                        setattr(course, key, value)
                session.commit()
                session.refresh(course)
            return course

    def delete_course(self, course_id: int):
        with Session(self.engine) as session:
            course = session.get(Course, course_id)
            if course:
                session.delete(course)
                session.commit()

    def list_courses(self) -> List[Course]:
        with Session(self.engine) as session:
            return session.query(Course).all()

    def list_courses_by_user(self, user_id: int) -> List[Course]:
        with Session(self.engine) as session:
            return session.query(Course).filter(Course.user_id == user_id).all()

    def list_courses_by_target_language(self, target_language: str) -> List[Course]:
        with Session(self.engine) as session:
            return session.query(Course).filter(Course.target_language == target_language).all()

    # ==================== LESSON CRUD ====================

    def insert_lesson(self, lesson: Lesson) -> Lesson:
        with Session(self.engine) as session:
            session.add(lesson)
            session.commit()
            session.refresh(lesson)
            return lesson

    def get_lesson(self, lesson_id: int) -> Optional[Lesson]:
        with Session(self.engine) as session:
            return session.get(Lesson, lesson_id)

    def update_lesson(self, lesson_id: int, **kwargs) -> Optional[Lesson]:
        with Session(self.engine) as session:
            lesson = session.get(Lesson, lesson_id)
            if lesson:
                for key, value in kwargs.items():
                    if hasattr(lesson, key):
                        setattr(lesson, key, value)
                session.commit()
                session.refresh(lesson)
            return lesson

    def delete_lesson(self, lesson_id: int):
        with Session(self.engine) as session:
            lesson = session.get(Lesson, lesson_id)
            if lesson:
                session.delete(lesson)
                session.commit()

    def list_lessons(self) -> List[Lesson]:
        with Session(self.engine) as session:
            return session.query(Lesson).all()

    def list_lessons_by_course(self, course_id: int) -> List[Lesson]:
        with Session(self.engine) as session:
            return session.query(Lesson).filter(Lesson.course_id == course_id).all()

    def list_lessons_by_user(self, user_id: int) -> List[Lesson]:
        with Session(self.engine) as session:
            return session.query(Lesson).filter(Lesson.user_id == user_id).all()

    def list_top_level_lessons(self, course_id: int) -> List[Lesson]:
        with Session(self.engine) as session:
            return session.query(Lesson).filter(
                Lesson.course_id == course_id,
                Lesson.parent_lesson_id.is_(None)
            ).all()

    # ==================== DICTIONARY ENTRY CRUD ====================

    def insert_dict_entry(self, entry: DictEntry) -> DictEntry:
        with Session(self.engine) as session:
            session.add(entry)
            session.commit()
            session.refresh(entry)
            return entry

    def get_dict_entry(self, entry_id: int) -> Optional[DictEntry]:
        with Session(self.engine) as session:
            return session.get(DictEntry, entry_id)

    def update_dict_entry(self, entry_id: int, **kwargs) -> Optional[DictEntry]:
        with Session(self.engine) as session:
            entry = session.get(DictEntry, entry_id)
            if entry:
                for key, value in kwargs.items():
                    if hasattr(entry, key):
                        setattr(entry, key, value)
                session.commit()
                session.refresh(entry)
            return entry

    def delete_dict_entry(self, entry_id: int):
        with Session(self.engine) as session:
            entry = session.get(DictEntry, entry_id)
            if entry:
                session.delete(entry)
                session.commit()

    def list_dict_entries(self) -> List[DictEntry]:
        with Session(self.engine) as session:
            return session.query(DictEntry).all()

    def list_dict_entries_by_language(self, language: str) -> List[DictEntry]:
        with Session(self.engine) as session:
            return session.query(DictEntry).filter(DictEntry.language == language).all()

    def get_dict_entry_by_lemma(self, language: str, lemma: str) -> Optional[DictEntry]:
        with Session(self.engine) as session:
            return session.scalar(
                select(DictEntry).where(
                    DictEntry.language == language,
                    DictEntry.lemma == lemma
                )
            )

    # ==================== DICTIONARY SENSE CRUD ====================

    def insert_dict_sense(self, sense: DictSense) -> DictSense:
        with Session(self.engine) as session:
            session.add(sense)
            session.commit()
            session.refresh(sense)
            return sense

    def get_dict_sense(self, sense_id: int) -> Optional[DictSense]:
        with Session(self.engine) as session:
            return session.get(DictSense, sense_id)

    def update_dict_sense(self, sense_id: int, **kwargs) -> Optional[DictSense]:
        with Session(self.engine) as session:
            sense = session.get(DictSense, sense_id)
            if sense:
                for key, value in kwargs.items():
                    if hasattr(sense, key):
                        setattr(sense, key, value)
                session.commit()
                session.refresh(sense)
            return sense

    def delete_dict_sense(self, sense_id: int):
        with Session(self.engine) as session:
            sense = session.get(DictSense, sense_id)
            if sense:
                session.delete(sense)
                session.commit()

    def list_dict_senses(self) -> List[DictSense]:
        with Session(self.engine) as session:
            return session.query(DictSense).all()

    def list_dict_senses_by_entry(self, entry_id: int) -> List[DictSense]:
        with Session(self.engine) as session:
            return session.query(DictSense).filter(DictSense.entry_id == entry_id).all()

    # ==================== DICTIONARY TRANSLATION CRUD ====================

    def insert_dict_translation(self, translation: DictTranslation) -> DictTranslation:
        with Session(self.engine) as session:
            session.add(translation)
            session.commit()
            session.refresh(translation)
            return translation

    def get_dict_translation(self, translation_id: int) -> Optional[DictTranslation]:
        with Session(self.engine) as session:
            return session.get(DictTranslation, translation_id)

    def update_dict_translation(self, translation_id: int, **kwargs) -> Optional[DictTranslation]:
        with Session(self.engine) as session:
            translation = session.get(DictTranslation, translation_id)
            if translation:
                for key, value in kwargs.items():
                    if hasattr(translation, key):
                        setattr(translation, key, value)
                session.commit()
                session.refresh(translation)
            return translation

    def delete_dict_translation(self, translation_id: int):
        with Session(self.engine) as session:
            translation = session.get(DictTranslation, translation_id)
            if translation:
                session.delete(translation)
                session.commit()

    def list_dict_translations(self) -> List[DictTranslation]:
        with Session(self.engine) as session:
            return session.query(DictTranslation).all()

    def list_dict_translations_by_sense(self, sense_id: int) -> List[DictTranslation]:
        with Session(self.engine) as session:
            return session.query(DictTranslation).filter(DictTranslation.sense_id == sense_id).all()

    def list_dict_translations_by_language(self, target_language: str) -> List[DictTranslation]:
        with Session(self.engine) as session:
            return session.query(DictTranslation).filter(DictTranslation.target_language == target_language).all()

    # ==================== DICTIONARY EXAMPLE CRUD ====================

    def insert_dict_example(self, example: DictExample) -> DictExample:
        with Session(self.engine) as session:
            session.add(example)
            session.commit()
            session.refresh(example)
            return example

    def get_dict_example(self, example_id: int) -> Optional[DictExample]:
        with Session(self.engine) as session:
            return session.get(DictExample, example_id)

    def update_dict_example(self, example_id: int, **kwargs) -> Optional[DictExample]:
        with Session(self.engine) as session:
            example = session.get(DictExample, example_id)
            if example:
                for key, value in kwargs.items():
                    if hasattr(example, key):
                        setattr(example, key, value)
                session.commit()
                session.refresh(example)
            return example

    def delete_dict_example(self, example_id: int):
        with Session(self.engine) as session:
            example = session.get(DictExample, example_id)
            if example:
                session.delete(example)
                session.commit()

    def list_dict_examples(self) -> List[DictExample]:
        with Session(self.engine) as session:
            return session.query(DictExample).all()

    def list_dict_examples_by_sense(self, sense_id: int) -> List[DictExample]:
        with Session(self.engine) as session:
            return session.query(DictExample).filter(DictExample.sense_id == sense_id).all()

    # ==================== USER SENSE STATE CRUD ====================

    def insert_user_sense_state(self, state: UserSenseState) -> UserSenseState:
        with Session(self.engine) as session:
            session.add(state)
            session.commit()
            session.refresh(state)
            return state

    def get_user_sense_state(self, user_id: int, sense_id: int) -> Optional[UserSenseState]:
        with Session(self.engine) as session:
            return session.get(UserSenseState, (user_id, sense_id))

    def update_user_sense_state(self, user_id: int, sense_id: int, **kwargs) -> Optional[UserSenseState]:
        with Session(self.engine) as session:
            state = session.get(UserSenseState, (user_id, sense_id))
            if state:
                for key, value in kwargs.items():
                    if hasattr(state, key):
                        setattr(state, key, value)
                session.commit()
                session.refresh(state)
            return state

    def delete_user_sense_state(self, user_id: int, sense_id: int):
        with Session(self.engine) as session:
            state = session.get(UserSenseState, (user_id, sense_id))
            if state:
                session.delete(state)
                session.commit()

    def list_user_sense_states(self, user_id: int) -> List[UserSenseState]:
        with Session(self.engine) as session:
            return session.query(UserSenseState).filter(UserSenseState.user_id == user_id).all()

    def list_user_sense_states_by_sense(self, sense_id: int) -> List[UserSenseState]:
        with Session(self.engine) as session:
            return session.query(UserSenseState).filter(UserSenseState.sense_id == sense_id).all()

    def ensure_settings_defaults(self, settings: json):
        self.ensure_entry(settings,'openAiKey', None)
        self.ensure_entry(settings,'openAiModel', 'gpt-3.5-turbo')
        self.ensure_entry(settings,'openAiTemperature', 0.7)
        self.ensure_entry(settings,'openAiSystemContent', "")
        self.ensure_entry(settings,'openAiUserContent', "")

    def ensure_entry(self, dictionary, key, default_value):
        """
        Ensures that the key exists in the dictionary.
        If the key doesn't exist, it adds it with the default value.
        """
        if key not in dictionary:
            dictionary[key] = default_value

    def load_settings(self) -> json:
        json_file_path = os.path.join(PROJECT_ROOT, "data", "settings.json")
        if os.path.isfile(json_file_path):
            with open(json_file_path, 'r') as f:
                settings = json.load(f)
                self.ensure_settings_defaults(settings)
                return settings
        else:
            with open(json_file_path, 'w') as f:
                settings = {'created': datetime.now().isoformat()}
                self.ensure_settings_defaults(settings)
                json.dump(settings, f, indent=4)
            return settings

    def save_settings(self, settings):
        json_file_path = os.path.join(PROJECT_ROOT, "data", "settings.json")
        self.ensure_settings_defaults(settings)
        with open(json_file_path, 'w') as f:
            json.dump(settings, f, indent=4)

    def get_setting(self, key:str):
        try:
            return self.load_settings()[key]
        except:
            return None

    def __del__(self):
        self.engine.dispose()

