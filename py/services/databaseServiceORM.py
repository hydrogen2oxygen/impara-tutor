import os
import sqlite3
from typing import List
from datetime import datetime
import json

from sqlalchemy import create_engine

from py.domains.ImparaDomains import User, UserCreate, LanguageCreate, Language

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

class ImparaDB:
    def __init__(self, db_filename):
        # Ensure the directory exists before connecting to the database
        db_dir = os.path.dirname(db_filename)
        os.makedirs(db_dir, exist_ok=True)
        self.engine = create_engine(f'sqlite:///{db_filename}', connect_args={'check_same_thread': False})

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

