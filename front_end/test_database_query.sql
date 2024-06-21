WITH assignment_completions AS (
    SELECT assignment_id,
           SUM(completed) AS num_completed,
           SUM(num_submissions) AS num_submissions
    FROM (
        SELECT s.assignment_id,
              e.exercise_id,
              IFNULL(MAX(s.passed), 0) = 1 OR (e.back_end = 'multiple_choice' AND COUNT(s.submission_id) > 0) AS completed,
              COUNT(submission_id) AS num_submissions
        FROM submissions s
        INNER JOIN exercises e
          ON s.exercise_id = e.exercise_id
        WHERE s.course_id = 37
          AND s.user_id = 'allyy'
          AND e.visible = 1
        GROUP BY s.assignment_id, s.exercise_id

        UNION

        SELECT assignment_id,
              exercise_id,
              0 AS num_completed,
              0 AS num_submissions
        FROM exercises
        WHERE course_id = 37
          AND visible = 1
    )
    GROUP BY assignment_id
),

assignment_num_exercises AS (
  SELECT assignment_id, COUNT(exercise_id) as num_exercises
  FROM exercises
  WHERE course_id = 37
    AND visible = 1
  GROUP BY assignment_id
),

assignment_scores AS (
    SELECT assignment_id, AVG(score) AS score
    FROM (
        SELECT assignment_id, exercise_id, MAX(score) AS score
        FROM (
            SELECT s.assignment_id, s.exercise_id, s.score
            FROM scores s
            INNER JOIN exercises e
              ON s.exercise_id = e.exercise_id
            WHERE s.course_id = 37
              AND s.user_id = 'allyy'
              AND e.visible = 1
            UNION

            SELECT assignment_id, exercise_id, 0
            FROM exercises
            WHERE course_id = 37
              AND visible = 1
        )
        GROUP BY exercise_id
    )
    GROUP BY assignment_id
),

assignment_statuses AS (
    SELECT a.assignment_id,
           a.title,
           a.visible,
           a.start_date,
           a.due_date,
           a.has_timer,
           a.hour_timer * 60 + minute_timer AS minutes_limit,
           a.restrict_other_assignments,
          (JulianDay(DATETIME('now')) - JulianDay(uas.start_time)) * 24 * 60 AS minutes_since_start,
           uas.ended_early,
           ac.num_completed,
           ac.num_submissions,
           ane.num_exercises,
           ats.score
    FROM assignments a
    INNER JOIN assignment_num_exercises ane
      ON a.assignment_id = ane.assignment_id
    INNER JOIN assignment_completions ac
      ON a.assignment_id = ac.assignment_id
    INNER JOIN assignment_scores ats
      ON a.assignment_id = ats.assignment_id
    LEFT JOIN user_assignment_starts uas
      ON a.course_id = uas.course_id
      AND a.assignment_id = uas.assignment_id
      AND a.has_timer = 1
      AND (uas.user_id = 'allyy' OR uas.user_id IS NULL)
    WHERE a.course_id = 37
      AND a.visible = 1
    ORDER BY a.title
)

SELECT *,
       IFNULL(minutes_since_start > minutes_limit OR ended_early, 0) AS timer_has_ended,
       IFNULL((num_submissions > 0 AND num_completed < num_exercises AND NOT has_timer) OR (has_timer AND minutes_since_start <= minutes_limit AND NOT ended_early), 0) AS in_progress,
       num_completed = num_exercises AS completed
FROM assignment_statuses