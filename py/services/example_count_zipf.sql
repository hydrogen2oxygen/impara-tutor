----------------------------------------------------------------------
-- A) GLOBAL FREQUENCY (per language)
--    Output: token, total_count across all lessons, rank, zipf_score=freq*rank
----------------------------------------------------------------------
WITH totals AS (
    SELECT
        t.id AS token_id,
        t.language,
        t.token_type,
        t.token,
        SUM(ltc.count_total) AS freq
    FROM lesson_token_count ltc
             JOIN token t ON t.id = ltc.token_id
    WHERE t.language = 'ru'
    GROUP BY t.id, t.language, t.token_type, t.token
),
     ranked AS (
         SELECT
             *,
             DENSE_RANK() OVER (ORDER BY freq DESC) AS rnk
         FROM totals
     )
SELECT
    language,
    token_type,
    token,
    freq,
    rnk AS rank,
    (freq * rnk) AS zipf_score,
    ROUND(1.0 * freq / SUM(freq) OVER (), 6) AS rel_freq
FROM ranked
ORDER BY freq DESC
LIMIT 200;


----------------------------------------------------------------------
-- B) FREQUENCY INSIDE ONE COURSE (per language)
--    Assumes lesson.course_id exists (as in your schema).
----------------------------------------------------------------------
WITH totals AS (
    SELECT
        t.id AS token_id,
        t.language,
        t.token_type,
        t.token,
        SUM(ltc.count_total) AS freq
    FROM lesson_token_count ltc
             JOIN token t   ON t.id = ltc.token_id
             JOIN lesson ls ON ls.id = ltc.lesson_id
    WHERE t.language = 'ru'
      AND ls.course_id = 1
    GROUP BY t.id, t.language, t.token_type, t.token
),
     ranked AS (
         SELECT
             *,
             DENSE_RANK() OVER (ORDER BY freq DESC) AS rnk
         FROM totals
     )
SELECT
    token_type,
    token,
    freq,
    rnk AS rank,
    (freq * rnk) AS zipf_score
FROM ranked
ORDER BY freq DESC
LIMIT 200;


----------------------------------------------------------------------
-- C) "IMPORTANT BUT NOT LEARNED" (requires token_dict_map)
--    Filters to tokens mapped to a dict_sense that the user does NOT yet have in user_sense_state.
--    Useful if you map tokens -> senses (or entries).
----------------------------------------------------------------------
WITH totals AS (
    SELECT
        t.id AS token_id,
        t.language,
        t.token_type,
        t.token,
        SUM(ltc.count_total) AS freq
    FROM lesson_token_count ltc
             JOIN token t ON t.id = ltc.token_id
    WHERE t.language = 'ru'
    GROUP BY t.id, t.language, t.token_type, t.token
),
     mapped AS (
         SELECT
             tot.*,
             m.sense_id
         FROM totals tot
                  JOIN token_dict_map m ON m.token_id = tot.token_id
         WHERE m.sense_id IS NOT NULL
     ),
     unknown AS (
         SELECT
             m.*
         FROM mapped m
                  LEFT JOIN user_sense_state us
                            ON us.user_id = 1
                                AND us.sense_id = m.sense_id
         WHERE us.sense_id IS NULL
     ),
     ranked AS (
         SELECT
             *,
             DENSE_RANK() OVER (ORDER BY freq DESC) AS rnk
         FROM unknown
     )
SELECT
    token_type,
    token,
    freq,
    rnk AS rank,
    (freq * rnk) AS zipf_score,
    sense_id
FROM ranked
ORDER BY freq DESC
LIMIT 200;


----------------------------------------------------------------------
-- D) LEARNING PRIORITY SCORE (frequency * novelty factor)
--    Example novelty: prefer tokens not learned OR learned at low SRS level.
--    Requires token_dict_map + user_sense_state.
----------------------------------------------------------------------
WITH totals AS (
    SELECT
        t.id AS token_id,
        t.language,
        t.token_type,
        t.token,
        SUM(ltc.count_total) AS freq
    FROM lesson_token_count ltc
             JOIN token t ON t.id = ltc.token_id
    WHERE t.language = 'ru'
    GROUP BY t.id, t.language, t.token_type, t.token
),
     mapped AS (
         SELECT
             tot.*,
             m.sense_id
         FROM totals tot
                  JOIN token_dict_map m ON m.token_id = tot.token_id
