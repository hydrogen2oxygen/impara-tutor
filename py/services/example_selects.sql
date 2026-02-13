------------------------------------------------------------
-- 1) FULL DICTIONARY VIEW (one lemma with full structure)
------------------------------------------------------------
SELECT
    e.language,
    e.lemma,
    s.sense_order,
    s.pos,
    s.gloss,
    t.target_language,
    t.translation,
    ex.example,
    ex.translation AS example_translation
FROM dict_entry e
         JOIN dict_sense s ON s.entry_id = e.id
         LEFT JOIN dict_translation t ON t.sense_id = s.id
         LEFT JOIN dict_example ex ON ex.sense_id = s.id
WHERE e.language = 'ru'
  AND e.lemma = 'ключ'
ORDER BY s.sense_order;


------------------------------------------------------------
-- 2) DICTIONARY SIZE PER LANGUAGE
------------------------------------------------------------
SELECT
    language,
    COUNT(*) AS total_entries
FROM dict_entry
GROUP BY language
ORDER BY total_entries DESC;


------------------------------------------------------------
-- 3) POLYSEMY REPORT (words with multiple senses)
------------------------------------------------------------
SELECT
    e.language,
    e.lemma,
    COUNT(s.id) AS number_of_senses
FROM dict_entry e
         JOIN dict_sense s ON s.entry_id = e.id
GROUP BY e.id
HAVING COUNT(s.id) > 1
ORDER BY number_of_senses DESC;


------------------------------------------------------------
-- 4) TRANSLATION DENSITY REPORT
------------------------------------------------------------
SELECT
    e.lemma,
    s.sense_order,
    COUNT(t.id) AS translation_count
FROM dict_entry e
         JOIN dict_sense s ON s.entry_id = e.id
         LEFT JOIN dict_translation t ON t.sense_id = s.id
GROUP BY s.id
ORDER BY translation_count DESC;


------------------------------------------------------------
-- 5) MISSING GERMAN TRANSLATIONS
------------------------------------------------------------
SELECT
    e.language,
    e.lemma,
    s.sense_order,
    s.gloss
FROM dict_sense s
         JOIN dict_entry e ON s.entry_id = e.id
         LEFT JOIN dict_translation t
                   ON t.sense_id = s.id AND t.target_language = 'de'
WHERE t.id IS NULL;


------------------------------------------------------------
-- 6) SENSES WITHOUT EXAMPLES
------------------------------------------------------------
SELECT
    e.language,
    e.lemma,
    s.sense_order,
    s.gloss
FROM dict_sense s
         JOIN dict_entry e ON s.entry_id = e.id
         LEFT JOIN dict_example ex ON ex.sense_id = s.id
WHERE ex.id IS NULL;


------------------------------------------------------------
-- 7) USER PROGRESS SUMMARY (user_id = 1)
------------------------------------------------------------
SELECT
    u.user_id,
    COUNT(u.sense_id) AS total_learned,
    AVG(u.srs_level) AS avg_srs_level,
    SUM(CASE WHEN u.next_due_at <= datetime('now') THEN 1 ELSE 0 END) AS due_now
FROM user_sense_state u
WHERE u.user_id = 1;


------------------------------------------------------------
-- 8) USER DUE ITEMS DETAIL (user_id = 1)
------------------------------------------------------------
SELECT
    e.language,
    e.lemma,
    s.sense_order,
    s.gloss,
    u.srs_level,
    u.next_due_at
FROM user_sense_state u
         JOIN dict_sense s ON s.id = u.sense_id
         JOIN dict_entry e ON e.id = s.entry_id
WHERE u.user_id = 1
  AND u.next_due_at <= datetime('now')
ORDER BY u.next_due_at;


------------------------------------------------------------
-- 9) MOST LEARNED LEMMAS (across users)
------------------------------------------------------------
SELECT
    e.lemma,
    COUNT(DISTINCT u.user_id) AS user_count
FROM user_sense_state u
         JOIN dict_sense s ON s.id = u.sense_id
         JOIN dict_entry e ON e.id = s.entry_id
GROUP BY e.id
ORDER BY user_count DESC;


------------------------------------------------------------
-- 10) LEMMA COMPLEXITY REPORT
------------------------------------------------------------
SELECT
    e.language,
    e.lemma,
    COUNT(DISTINCT s.id) AS sense_count,
    COUNT(DISTINCT ex.id) AS example_count
FROM dict_entry e
         LEFT JOIN dict_sense s ON s.entry_id = e.id
         LEFT JOIN dict_example ex ON ex.sense_id = s.id
GROUP BY e.id
ORDER BY sense_count DESC;
