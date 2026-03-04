import os
from typing import List
from datetime import datetime
import json

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from py.domains.ImparaDomainsORM import User, Language, Languages, Base

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

    def sql_select(self, sql:str):
        cursor = self.conn.execute(sql)
        # Get column names from cursor description
        column_names = [desc[0] for desc in cursor.description]
        # Fetch all rows as dictionaries
        rows = [dict(zip(column_names, row)) for row in cursor.fetchall()]
        # Prepare the final JSON structure
        result = {
            "sql": sql,
            "columns": column_names,
            "data": rows
        }
        return result

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
        self.conn.close()

