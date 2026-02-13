----------------------------------------------------------------------
-- 1) Token catalog (normalized word/phrase inventory per language)
--    Stores words and multi-word phrases you’ve extracted from lessons.
----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS token (
id          INTEGER PRIMARY KEY AUTOINCREMENT,
language    TEXT NOT NULL,            -- ISO code, e.g. 'ru'
token       TEXT NOT NULL,            -- surface form: 'ключ', 'по крайней мере'
normalized  TEXT,                     -- lowercase/stripped for search
token_type  TEXT NOT NULL DEFAULT 'word',  -- 'word' | 'phrase'
ngrams      INTEGER NOT NULL DEFAULT 1,    -- 1 for word, 2+ for phrase
created_at  TEXT NOT NULL DEFAULT (datetime('now')),
UNIQUE(language, token, token_type)
);

CREATE INDEX IF NOT EXISTS idx_token_lang_norm ON token(language, normalized);
CREATE INDEX IF NOT EXISTS idx_token_type ON token(token_type);


----------------------------------------------------------------------
-- 2) Lesson token counts (bag-of-words / bag-of-phrases per lesson)
--    One row per (lesson, token). Supports word counts, phrase counts.
----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS lesson_token_count (
lesson_id        INTEGER NOT NULL REFERENCES lesson(id) ON DELETE CASCADE,
token_id         INTEGER NOT NULL REFERENCES token(id) ON DELETE CASCADE,
count_total      INTEGER NOT NULL DEFAULT 0,  -- total occurrences in lesson text
count_unique     INTEGER NOT NULL DEFAULT 0,  -- optional: 0/1 if present, or unique occurrences
first_pos        INTEGER,                     -- optional: first character index in text
last_pos         INTEGER,                     -- optional: last character index in text
computed_at      TEXT NOT NULL DEFAULT (datetime('now')),
PRIMARY KEY (lesson_id, token_id)
);

CREATE INDEX IF NOT EXISTS idx_ltc_token ON lesson_token_count(token_id);
CREATE INDEX IF NOT EXISTS idx_ltc_lesson ON lesson_token_count(lesson_id);


----------------------------------------------------------------------
-- 3) Optional: exact occurrences (for highlighting / concordance)
--    If you want to highlight each match in the lesson text.
----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS lesson_token_occurrence (
id         INTEGER PRIMARY KEY AUTOINCREMENT,
lesson_id  INTEGER NOT NULL REFERENCES lesson(id) ON DELETE CASCADE,
token_id   INTEGER NOT NULL REFERENCES token(id) ON DELETE CASCADE,
start_pos  INTEGER NOT NULL,      -- character offset in lesson.text
end_pos    INTEGER NOT NULL,      -- exclusive end offset
matched    TEXT NOT NULL          -- exact matched substring
);

CREATE INDEX IF NOT EXISTS idx_lto_lesson ON lesson_token_occurrence(lesson_id);
CREATE INDEX IF NOT EXISTS idx_lto_token ON lesson_token_occurrence(token_id);


----------------------------------------------------------------------
-- 4) Optional: lesson stats (quick report without recomputing)
--    Good for dashboards: total words, unique words, total phrases, etc.
----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS lesson_lex_stats (
lesson_id              INTEGER PRIMARY KEY REFERENCES lesson(id) ON DELETE CASCADE,
language               TEXT NOT NULL,
words_total            INTEGER NOT NULL DEFAULT 0,
words_unique           INTEGER NOT NULL DEFAULT 0,
phrases_total          INTEGER NOT NULL DEFAULT 0,
phrases_unique         INTEGER NOT NULL DEFAULT 0,
chars_total            INTEGER NOT NULL DEFAULT 0,
computed_at            TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_lls_lang ON lesson_lex_stats(language);


----------------------------------------------------------------------
-- 5) Optional: connect extracted tokens to dictionary senses (if desired)
--    Lets you say “this token corresponds to these dict_entry/sense ids”.
----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS token_dict_map (
token_id     INTEGER NOT NULL REFERENCES token(id) ON DELETE CASCADE,
entry_id     INTEGER REFERENCES dict_entry(id) ON DELETE SET NULL,
sense_id     INTEGER REFERENCES dict_sense(id) ON DELETE SET NULL,
confidence   REAL,                 -- optional, e.g. 0.0..1.0
note         TEXT,
PRIMARY KEY (token_id, entry_id, sense_id)
);

CREATE INDEX IF NOT EXISTS idx_tdm_entry ON token_dict_map(entry_id);
CREATE INDEX IF NOT EXISTS idx_tdm_sense ON token_dict_map(sense_id);
