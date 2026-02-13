import os
import sqlite3
from typing import List
from datetime import datetime
import json

from py.domains.ImparaDomains import User, UserCreate, LanguageCreate, Language

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

class ImparaDB:
    def __init__(self, db_filename):
        # Ensure the directory exists before connecting to the database
        db_dir = os.path.dirname(db_filename)
        os.makedirs(db_dir, exist_ok=True)

        self.conn = sqlite3.connect(db_filename, isolation_level=None, timeout=10, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute('PRAGMA journal_mode = WAL;')
        self.conn.execute('PRAGMA foreign_keys = ON;')
        self.create_table()

    def close(self):
        self.conn.close()

    def create_table(self):
        # User learning languages and courses
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS user
            (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                display_name   TEXT NOT NULL,
                email          TEXT,
                bio            TEXT,
                avatar_path    TEXT,
                created_at     TEXT NOT NULL DEFAULT (datetime('now')),
                last_active_at TEXT NOT NULL DEFAULT (datetime('now')),
                UNIQUE(display_name)
            );
        ''')
        # Each user can have multiple language pairs (source-target) they are learning
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS language
            (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER NOT NULL,
                source_language TEXT NOT NULL,
                target_language TEXT NOT NULL,
                created_at      TEXT NOT NULL DEFAULT (datetime('now')),
                UNIQUE(user_id, source_language, target_language)
            );
        ''')
        # Global list of languages for dropdowns, etc. ISO code + name
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS languages
            (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                UNIQUE(code, name)
            );
        ''')
        # Courses created by users, each course is for a specific target language and has multiple lessons
        self.conn.execute('''
           CREATE TABLE IF NOT EXISTS course
           (
               id              INTEGER PRIMARY KEY AUTOINCREMENT,
               user_id         INTEGER NOT NULL,
               target_language TEXT NOT NULL,
               title           TEXT NOT NULL,
               description     TEXT,
               source_link     TEXT,
               tags            TEXT,
               created_at      TEXT NOT NULL DEFAULT (datetime('now')),
               UNIQUE(target_language, title)
           ); 
        ''')
        # Lessons belong to courses, each lesson has a title, description, text content, and optional source link and tags
        # parent_lesson_id allows for nested lessons (e.g. a lesson with sub-lessons), but can be NULL for top-level lessons
        self.conn.execute('''
              CREATE TABLE IF NOT EXISTS lesson
              (
                  id               INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id          INTEGER NOT NULL,
                  course_id        INTEGER NOT NULL,
                  parent_lesson_id INTEGER, -- for nested lessons
                  title            TEXT    NOT NULL,
                  description      TEXT,
                  text             TEXT,
                  source_link      TEXT,
                  tags             TEXT,
                  created_at       TEXT    NOT NULL DEFAULT (datetime('now')),
                  UNIQUE (course_id, title)
              ); 
        ''')
        # DICTIONARY TABLES
        # A dictionary entry is a lemma in a specific language, with optional IPA and normalized form for search.
        self.conn.execute('''
                CREATE TABLE IF NOT EXISTS dict_entry
                (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    language   TEXT NOT NULL, -- ISO code: 'ru', 'de', ...
                    lemma      TEXT NOT NULL, -- canonical form
                    normalized TEXT,          -- optional: lowercase/stripped for search
                    ipa        TEXT,          -- optional pronunciation
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    UNIQUE (language, lemma)
                ); 
        ''')
        # A sense is a specific meaning of a lemma, with part of speech, gloss, and usage notes. Each sense belongs to one dict_entry.
        self.conn.execute('''
                CREATE TABLE IF NOT EXISTS dict_sense
                (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    entry_id    INTEGER NOT NULL REFERENCES dict_entry (id) ON DELETE CASCADE,
                    pos         TEXT,    -- noun/verb/adj...
                    gloss       TEXT,    -- short definition in same language or meta-language
                    note        TEXT,    -- usage notes
                    sense_order INTEGER, -- 1..n for display
                    UNIQUE (entry_id, sense_order)
                );
        ''')
        self.conn.execute('''CREATE INDEX IF NOT EXISTS idx_sense_entry ON dict_sense (entry_id);''')
        # A translation links a sense to a translation in a target language, with an optional note for context. Each sense can have multiple translations.
        self.conn.execute('''
                CREATE TABLE IF NOT EXISTS dict_translation
                (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    sense_id        INTEGER NOT NULL REFERENCES dict_sense (id) ON DELETE CASCADE,
                    target_language TEXT    NOT NULL, -- ISO code
                    translation     TEXT    NOT NULL,
                    note            TEXT,             -- context-specific note
                    UNIQUE (sense_id, target_language, translation)
                );
        ''')
        self.conn.execute('''CREATE INDEX IF NOT EXISTS idx_tr_sense ON dict_translation (sense_id);''')
        self.conn.execute('''CREATE INDEX IF NOT EXISTS idx_tr_lang ON dict_translation (target_language, translation);''')
        # An example sentence for a sense, with optional translation and source. Each sense can have multiple examples.
        self.conn.execute('''
                CREATE TABLE IF NOT EXISTS dict_example
                (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    sense_id    INTEGER NOT NULL REFERENCES dict_sense (id) ON DELETE CASCADE,
                    example     TEXT    NOT NULL,
                    translation TEXT,
                    source      TEXT
                );
        ''')
        self.conn.execute('''CREATE INDEX IF NOT EXISTS idx_ex_sense ON dict_example (sense_id);''')
        # User-specific learning state for each sense, tracking SRS level, last seen, and next due dates. Each user can have one entry per sense.
        self.conn.execute('''
                CREATE TABLE IF NOT EXISTS user_sense_state
                (
                    user_id      INTEGER NOT NULL,
                    sense_id     INTEGER NOT NULL REFERENCES dict_sense (id) ON DELETE CASCADE,
                    srs_level    INTEGER NOT NULL DEFAULT 0,
                    last_seen_at TEXT,
                    next_due_at  TEXT,
                    PRIMARY KEY (user_id, sense_id)
                );
        ''')

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

        self.conn.executemany(
            "INSERT OR IGNORE INTO languages (code, name) VALUES (?, ?)",
            language_list
        )

        self.conn.commit()

    def insert_user(self, user: UserCreate):
        query = '''
        INSERT INTO user (display_name, email, bio, avatar_path, created_at, last_active_at)
        VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
        '''
        self.conn.execute(query, (user.display_name, user.email, user.bio, user.avatar_path))
        self.conn.commit()

    def get_user(self, id: int) -> User | None:
        row = self.conn.execute(
            'SELECT id, display_name, email, bio, avatar_path, created_at, last_active_at FROM user WHERE id = ?',
            (id,)
        ).fetchone()

        if row:
            return User(
                id=row[0],
                display_name=row[1],
                email=row[2],
                bio=row[3],
                avatar_path=row[4],
                created_at=row[5],
                last_active_at=row[6],
            )
        return None

    def get_user_by_name(self, name: str) -> User | None:
        row = self.conn.execute('SELECT * FROM user WHERE display_name = ?', (name,)).fetchone()
        if row:
            return User(
                id=row[0],
                display_name=row[1],
                email=row[2],
                bio=row[3],
                avatar_path=row[4],
                created_at=row[5],
                last_active_at=row[6],
            )
        return None

    def delete_user(self, user_id: int):
        query = 'DELETE FROM user WHERE id = ?'
        self.conn.execute(query, (user_id,))
        self.conn.commit()

    def list_users(self) -> List[User]:
        cur = self.conn.execute(
            "SELECT id, display_name, email, bio, avatar_path, created_at, last_active_at FROM user"
        )

        rows = cur.fetchmany(500)

        return [
                {
                    "id": r["id"],
                    "display_name": r["display_name"],
                    "email": r["email"],
                    "bio": r["bio"],
                    "avatar_path": r["avatar_path"],
                    "created_at": r["created_at"],
                    "last_active_at": r["last_active_at"],
                }
                for r in rows
            ]

    def list_languages(self) -> []:
        cur = self.conn.execute("SELECT code, name FROM languages ORDER BY name")
        rows = cur.fetchall()
        return [
            {
                "code": r["code"],
                "name": r["name"]
            }
            for r in rows
        ]

    def insert_language(self, language: LanguageCreate):
        query = '''
        INSERT INTO language (user_id, source_language, target_language, created_at)
        VALUES (?, ?, ?, datetime('now'))
        '''
        self.conn.execute(query, (language.user_id, language.source_language, language.target_language))
        self.conn.commit()

    def list_user_languages(self, user_id: int) -> List[Language]:
        cur = self.conn.execute(
            'SELECT id, user_id, source_language, target_language, created_at FROM language WHERE user_id = ?',
            (user_id,)
        )
        rows = cur.fetchall()
        return [
                    {
                        "id": r["id"],
                        "user_id": r["user_id"],
                        "source_language": r["source_language"],
                        "target_language": r["target_language"],
                        "created_at": r["created_at"]
                    }
                    for r in rows
                ]

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

