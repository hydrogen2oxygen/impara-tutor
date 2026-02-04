import os
import sqlite3
from typing import List
from datetime import datetime
import json

from flask import jsonify

from py.domains.ImparaDomains import User

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

class ImparaDAO:
    def __init__(self, db_filename):
        self.conn = sqlite3.connect(db_filename, isolation_level=None, timeout=10, check_same_thread=False)
        self.conn.execute('PRAGMA journal_mode = WAL;')
        self.conn.execute('PRAGMA foreign_keys = ON;')
        self.create_table()

    def close(self):
        self.conn.close()

    def create_table(self):
        user_query = '''
            CREATE TABLE user
            (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                display_name   TEXT NOT NULL,
                email          TEXT,
                bio            TEXT,
                avatar_path    TEXT,

                created_at     TEXT NOT NULL DEFAULT (datetime('now')),
                last_active_at TEXT
            );
        '''
        self.conn.execute(user_query)
        self.conn.commit()

    def insert_user(self, user: User):
        query = '''
        INSERT INTO user (display_name, email, bio, avatar_path, created_at, last_active_at)
        VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
        '''
        self.conn.execute(query, (user.display_name, user.email, user.bio, user.avatar_path))
        self.conn.commit()

    def get_user(self, id: int) -> User | None:
        row = self.conn.execute('SELECT * FROM user WHERE id = ?', (id,)).fetchone()
        if row:
            user = User(row[1], row[2], row[3], row[4], row[5], row[6], row[7])
            user.id = row[0]
            return user
        return None

    def get_user_by_name(self, name: str) -> User | None:
        row = self.conn.execute('SELECT * FROM user WHERE name = ?', (name,)).fetchone()
        if row:
            user = User(row[1], row[2], row[3], row[4], row[5], row[6], row[7])
            user.id = row[0]
            return user
        return None

    def delete_user(self, user_id: int):
        query = 'DELETE FROM user WHERE id = ?'
        self.conn.execute(query, (user_id,))
        self.conn.commit()

    def list_users(self) -> List[User]:
        cursor = self.conn.execute('SELECT * FROM user')
        users = []
        for row in cursor:
            user = User(row[1], row[2], row[3], row[4], row[5], row[6], row[7])
            user.id = row[0]
            users.append(user)
        return users

    def sqlSelect(self, sql:str):
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

    def loadSettings(self) -> json:
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
                json.dump(settings, f)
            return jsonify(settings)

    def saveSettings(self, settings):
        json_file_path = os.path.join(PROJECT_ROOT, "data", "settings.json")
        self.ensure_settings_defaults(settings)
        with open(json_file_path, 'w') as f:
            json.dump(settings, f, indent=4)

    def get_setting(self, key:str):
        try:
            return self.loadSettings()[key]
        except:
            return None

    def __del__(self):
        self.conn.close()

# DAO Service to be imported into another class
def get_case_dao(db_filename: str) -> ImparaDAO:
    return ImparaDAO(db_filename)
