WITH
  variables AS (
    SELECT
      ? AS course_id,
      ? AS assignment_id,
      ? AS exercise_id,
      ? AS user_id
  ),

  valid_assignments AS (
    SELECT
      assignment_id,
      title,
      visible,
      start_date,
      due_date,
      has_timer,
      hour_timer,
      minute_timer,
      restrict_other_assignments,
      custom_scoring,
      assignment_group_id
    FROM assignments
    WHERE course_id = (SELECT course_id FROM variables)
      AND (
        (SELECT assignment_id FROM variables) IS NULL
        OR assignment_id = (SELECT assignment_id FROM variables)
      )
  ),

  valid_assignment_groups AS (
    SELECT
      assignment_group_id,
      title
    FROM assignment_groups
    WHERE course_id = (SELECT course_id FROM variables)
  ),

  valid_exercises AS (
    SELECT
      e.assignment_id,
      e.exercise_id,
      e.title,
      e.visible,
      e.back_end,
      e.enable_pair_programming,
      e.weight,
      e.back_end = 'multiple_choice' AS is_multiple_choice
    FROM exercises e
    INNER JOIN valid_assignments a
      ON e.assignment_id = a.assignment_id
    WHERE e.course_id = (SELECT course_id FROM variables)
      AND e.assignment_id IN (SELECT assignment_id FROM valid_assignments)
	    AND (
        (SELECT exercise_id FROM variables) IS NULL
        OR exercise_id = (SELECT exercise_id FROM variables)
      )
  ),

  valid_users AS (
    SELECT
      u.user_id,
      u.name
    FROM course_registrations cr
    INNER JOIN users u
      ON cr.user_id = u.user_id
    WHERE cr.course_id = (SELECT course_id FROM variables)
      AND (
        (SELECT user_id FROM variables) IS NULL
        OR u.user_id = (SELECT user_id FROM variables)
      )
      AND u.user_id NOT IN (
        SELECT user_id
        FROM permissions
        WHERE course_id = 0 OR course_id = (SELECT course_id FROM variables)
      )
  ),

  valid_submissions AS (
    SELECT
      s.course_id,
      s.assignment_id,
      s.exercise_id,
      s.user_id,
      s.submission_id,
      s.code,
      s.passed,
      (s.passed OR e.is_multiple_choice) AS completed,
      s.date AS submission_timestamp,
      s.partner_id
    FROM submissions s
    INNER JOIN valid_exercises e
      ON s.assignment_id = e.assignment_id
      AND s.exercise_id = e.exercise_id
    WHERE s.course_id = (SELECT course_id FROM variables)
      -- AND s.assignment_id IN (SELECT assignment_id FROM valid_assignments)
      -- AND exercise_id IN (SELECT exercise_id FROM valid_exercises)
      AND s.user_id IN (SELECT user_id FROM valid_users)
      AND e.visible = 1
  ),

  exercise_statuses AS (
    SELECT
      assignment_id,
      exercise_id,
      user_id,
      MAX(completed) AS completed,
      MAX(num_submissions) AS num_submissions,
      MAX(completed) = 0 AND MAX(num_submissions) > 0 AS in_progress,
      MAX(pair_programmed) AS pair_programmed,
      MAX(last_submission_timestamp) AS last_submission_timestamp
    FROM (
      SELECT
        s.assignment_id,
        s.exercise_id,
        s.user_id,
        MAX(s.completed) AS completed,
        COUNT(s.submission_id) AS num_submissions,
        COUNT(s.partner_id) > 0 AS pair_programmed,
        MAX(s.submission_timestamp) AS last_submission_timestamp
      FROM valid_submissions s
      GROUP BY s.assignment_id, s.exercise_id, s.user_id

      UNION

      SELECT
        e.assignment_id,
        e.exercise_id,
        u.user_id,
        0 AS completed,
        0 AS num_submissions,
        0 AS pair_programmed,
        NULL AS last_submission_timestamp
      FROM valid_exercises e
      INNER JOIN valid_users u
      WHERE e.visible = 1
    )
    GROUP BY assignment_id, exercise_id, user_id
  ),

  exercise_scores_weights AS (
    SELECT
      es.assignment_id,
      es.exercise_id,
      es.user_id,
      IFNULL(s.score, 0) AS score,
      e.weight
    FROM exercise_statuses es
    INNER JOIN exercises e
      ON es.assignment_id = e.assignment_id
      AND es.exercise_id = e.exercise_id
    LEFT JOIN scores s
      ON es.assignment_id = s.assignment_id
      AND es.exercise_id = s.exercise_id
      AND es.user_id = s.user_id
    WHERE e.visible = 1
  ),

  latest_completed_submissions AS (
    SELECT
      assignment_id,
      exercise_id,
      user_id,
      submission_id,
      code,
      submission_timestamp,
      partner_id
    FROM valid_submissions
    WHERE completed = 1
    GROUP BY assignment_id, exercise_id, user_id
    HAVING MAX(submission_timestamp)
  ),

  latest_submissions AS (
    SELECT
      MAX(assignment_id) AS assignment_id,
      MAX(exercise_id) AS exercise_id,
      MAX(user_id) AS user_id,
      MAX(submission_id) AS submission_id,
      MAX(code) AS code,
      MAX(submission_timestamp) AS submission_timestamp,
      MAX(partner_id) AS partner_id
    FROM (
      SELECT
        assignment_id,
        exercise_id,
        user_id,
        submission_id,
        code,
        submission_timestamp,
        partner_id
      FROM valid_submissions
      GROUP BY assignment_id, exercise_id, user_id
      HAVING MAX(submission_timestamp)

      UNION

      SELECT
        e.assignment_id,
        e.exercise_id,
        u.user_id,
        NULL AS submission_id,
        NULL AS code,
        NULL AS submission_timestamp,
        NULL AS partner_id
      FROM valid_exercises e
      INNER JOIN valid_users u
    )
    GROUP BY assignment_id, exercise_id, user_id
  ),

  assignments_num_exercises AS (
    SELECT
      assignment_id,
      COUNT(exercise_id) as num_exercises
    FROM valid_exercises
    WHERE visible = 1
    GROUP BY assignment_id
  ),

  assignment_scores AS (
    SELECT
      es.assignment_id,
      es.user_id,
      adjust_assignment_score(ROUND(AVG(esw.score * esw.weight) / AVG(esw.weight), 2), a.custom_scoring) AS score
    FROM exercise_statuses es
    INNER JOIN exercise_scores_weights esw
      ON es.assignment_id = esw.assignment_id
      AND es.exercise_id = esw.exercise_id
      AND es.user_id = esw.user_id
    INNER JOIN valid_assignments a
      ON es.assignment_id = a.assignment_id
    WHERE a.visible = 1
    GROUP BY es.assignment_id, es.user_id
  ),

  assignment_timer_statuses AS (
    SELECT
      a.assignment_id,
      uas.user_id,
      a.hour_timer * 60 + minute_timer AS minutes_limit,
      (JulianDay(DATETIME('now')) - JulianDay(uas.start_time)) * 24 * 60 AS minutes_since_start,
      uas.ended_early
    FROM valid_assignments a
    LEFT JOIN user_assignment_starts uas
      ON a.assignment_id = uas.assignment_id
      AND a.has_timer = 1
      AND uas.user_id IN (SELECT user_id FROM valid_users)
    WHERE uas.course_id = (SELECT course_id FROM variables)
      AND a.visible = 1
  ),

  assignment_statuses AS (
    SELECT
      es.assignment_id,
      es.user_id,
      ane.num_exercises,
      a.start_date,
      a.due_date,
      a.has_timer,
      SUM(es.completed) AS num_completed,
      SUM(es.completed) = ane.num_exercises AS completed,
      IFNULL((NOT a.has_timer AND SUM(es.num_submissions) > 0 AND SUM(es.completed) < ane.num_exercises) OR (a.has_timer AND ats.minutes_since_start <= ats.minutes_limit AND NOT ats.ended_early), 0) AS in_progress,
      IFNULL(ats.minutes_since_start > ats.minutes_limit OR ats.ended_early, 0) AS timer_has_ended,
      SUM(pair_programmed) AS num_times_pair_programmed,
      MAX(last_submission_timestamp) AS last_submission_timestamp
    FROM exercise_statuses es
    INNER JOIN valid_assignments a
      ON es.assignment_id = a.assignment_id
    INNER JOIN assignments_num_exercises ane
      ON es.assignment_id = ane.assignment_id
    LEFT JOIN assignment_timer_statuses ats
      ON es.assignment_id = ats.assignment_id
      AND es.user_id = ats.user_id
    GROUP BY es.assignment_id, es.user_id
  )