BEGIN TRANSACTION;

------------------------------------------------------------
-- ENTRY 1: ключ (ru)
------------------------------------------------------------
INSERT INTO dict_entry (language, lemma, normalized, ipa)
VALUES ('ru', 'ключ', 'ключ', 'klʲut͡ɕ');

-- SENSES
INSERT INTO dict_sense (entry_id, pos, gloss, sense_order)
VALUES
    ((SELECT id FROM dict_entry WHERE language='ru' AND lemma='ключ'),
     'noun', 'instrument for opening locks', 1),

    ((SELECT id FROM dict_entry WHERE language='ru' AND lemma='ключ'),
     'noun', 'natural water source', 2),

    ((SELECT id FROM dict_entry WHERE language='ru' AND lemma='ключ'),
     'noun', 'solution or clue to a problem', 3);

-- TRANSLATIONS
INSERT INTO dict_translation (sense_id, target_language, translation)
VALUES
-- sense 1
((SELECT s.id FROM dict_sense s
                       JOIN dict_entry e ON s.entry_id = e.id
  WHERE e.lemma='ключ' AND s.sense_order=1),
 'de', 'Schlüssel'),

((SELECT s.id FROM dict_sense s
                       JOIN dict_entry e ON s.entry_id = e.id
  WHERE e.lemma='ключ' AND s.sense_order=1),
 'en', 'key'),

-- sense 2
((SELECT s.id FROM dict_sense s
                       JOIN dict_entry e ON s.entry_id = e.id
  WHERE e.lemma='ключ' AND s.sense_order=2),
 'de', 'Quelle'),

((SELECT s.id FROM dict_sense s
                       JOIN dict_entry e ON s.entry_id = e.id
  WHERE e.lemma='ключ' AND s.sense_order=2),
 'en', 'spring'),

-- sense 3
((SELECT s.id FROM dict_sense s
                       JOIN dict_entry e ON s.entry_id = e.id
  WHERE e.lemma='ключ' AND s.sense_order=3),
 'de', 'Hinweis'),

((SELECT s.id FROM dict_sense s
                       JOIN dict_entry e ON s.entry_id = e.id
  WHERE e.lemma='ключ' AND s.sense_order=3),
 'en', 'clue');

-- EXAMPLES
INSERT INTO dict_example (sense_id, example, translation)
VALUES
    ((SELECT s.id FROM dict_sense s
                           JOIN dict_entry e ON s.entry_id = e.id
      WHERE e.lemma='ключ' AND s.sense_order=1),
     'Я потерял ключ.',
     'Ich habe den Schlüssel verloren.'),

    ((SELECT s.id FROM dict_sense s
                           JOIN dict_entry e ON s.entry_id = e.id
      WHERE e.lemma='ключ' AND s.sense_order=2),
     'Мы нашли горный ключ.',
     'Wir haben eine Bergquelle gefunden.'),

    ((SELECT s.id FROM dict_sense s
                           JOIN dict_entry e ON s.entry_id = e.id
      WHERE e.lemma='ключ' AND s.sense_order=3),
     'Это ключ к решению проблемы.',
     'Das ist der Schlüssel zur Lösung des Problems.');

------------------------------------------------------------
-- ENTRY 2: идти (ru)
------------------------------------------------------------
INSERT INTO dict_entry (language, lemma, normalized, ipa)
VALUES ('ru', 'идти', 'идти', 'ɪdʲˈtʲi');

INSERT INTO dict_sense (entry_id, pos, gloss, note, sense_order)
VALUES
    ((SELECT id FROM dict_entry WHERE language='ru' AND lemma='идти'),
     'verb', 'to go on foot (imperfective)', 'movement by foot', 1);

INSERT INTO dict_translation (sense_id, target_language, translation, note)
VALUES
    ((SELECT s.id FROM dict_sense s
                           JOIN dict_entry e ON s.entry_id = e.id
      WHERE e.lemma='идти'),
     'de', 'gehen', 'zu Fuß'),

    ((SELECT s.id FROM dict_sense s
                           JOIN dict_entry e ON s.entry_id = e.id
      WHERE e.lemma='идти'),
     'en', 'to go', 'by foot');

INSERT INTO dict_example (sense_id, example, translation)
VALUES
    ((SELECT s.id FROM dict_sense s
                           JOIN dict_entry e ON s.entry_id = e.id
      WHERE e.lemma='идти'),
     'Я иду домой.',
     'Ich gehe nach Hause.');

------------------------------------------------------------
-- ENTRY 3: Bank (de)
------------------------------------------------------------
INSERT INTO dict_entry (language, lemma, normalized)
VALUES ('de', 'Bank', 'bank');

INSERT INTO dict_sense (entry_id, pos, gloss, sense_order)
VALUES
    ((SELECT id FROM dict_entry WHERE language='de' AND lemma='Bank'),
     'noun', 'financial institution', 1),

    ((SELECT id FROM dict_entry WHERE language='de' AND lemma='Bank'),
     'noun', 'bench for sitting', 2);

INSERT INTO dict_translation (sense_id, target_language, translation)
VALUES
    ((SELECT s.id FROM dict_sense s
                           JOIN dict_entry e ON s.entry_id = e.id
      WHERE e.lemma='Bank' AND s.sense_order=1),
     'en', 'bank'),

    ((SELECT s.id FROM dict_sense s
                           JOIN dict_entry e ON s.entry_id = e.id
      WHERE e.lemma='Bank' AND s.sense_order=2),
     'en', 'bench');

------------------------------------------------------------
-- USER SRS STATE (user_id = 1)
------------------------------------------------------------
INSERT INTO user_sense_state
(user_id, sense_id, srs_level, last_seen_at, next_due_at)
VALUES
    (1,
     (SELECT s.id FROM dict_sense s
                           JOIN dict_entry e ON s.entry_id = e.id
      WHERE e.lemma='ключ' AND s.sense_order=1),
     2, datetime('now'), datetime('now','+3 days')),

    (1,
     (SELECT s.id FROM dict_sense s
                           JOIN dict_entry e ON s.entry_id = e.id
      WHERE e.lemma='ключ' AND s.sense_order=3),
     1, datetime('now'), datetime('now','+1 day')),

    (1,
     (SELECT s.id FROM dict_sense s
                           JOIN dict_entry e ON s.entry_id = e.id
      WHERE e.lemma='идти'),
     4, datetime('now'), datetime('now','+7 days'));

COMMIT;
