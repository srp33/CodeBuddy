# Returns the number of non-admin, non-instructor, non-assistant students
# in a given course.
def students_course(course_id):
    return f'''SELECT DISTINCT user_id
               FROM users
               WHERE user_id NOT IN
               (
                 SELECT user_id
                 FROM permissions
                 WHERE course_id = 0 OR course_id = {course_id}
               )'''

# Identifies which problems are visible for a given course.
def visible_problems_course(course_id):
    return f'''SELECT assignment_id, problem_id, title
               FROM problems
               WHERE course_id = {course_id}
                 AND visible = 1'''

# Calculates the number of problems are visible for a given course.
def num_visible_problems_course(course_id):
    return f'''SELECT assignment_id, COUNT(problem_id) as problem_count
               FROM ({visible_problems_course(course_id)})
               GROUP BY assignment_id'''

# Identifies which assignments are visible for a given course.
def visible_assignments_course(course_id):
    return f'''SELECT assignment_id, title
               FROM assignments
               WHERE course_id = {course_id}
                 AND visible = 1'''

# Identifies whether each student has passed each problem that they have attempted
# for a given course.
def user_problem_status_course(course_id):
    return f'''SELECT s.assignment_id, s.problem_id, s.user_id, MAX(s.passed) AS passed
               FROM submissions s
               INNER JOIN ({visible_problems_course(course_id)}) p
                 ON s.assignment_id = p.assignment_id
                 AND s.problem_id = p.problem_id
               INNER JOIN ({visible_assignments_course(course_id)}) a
                 ON s.assignment_id = a.assignment_id
               INNER JOIN ({students_course(course_id)}) st
                 ON s.user_id = st.user_id
               WHERE s.course_id = {course_id}
               GROUP BY s.assignment_id, s.problem_id, s.user_id'''

# Calculates the average score across all students for each assignment in a course,
# as well as the number of students who have completed each assignment and the number
# of students total for the course.
def assignment_summary_course(course_id):
    return f'''WITH const
               AS (SELECT COUNT(*) AS num_students FROM ({students_course(course_id)}))

               SELECT a.assignment_id,
                      a.title,
                      IFNULL(b.num_passed, 0) AS num_students_completed,
                      const.num_students AS num_students,
                      ROUND(IFNULL(b.total_percent, 0) / const.num_students, 1) AS avg_score
               FROM ({visible_assignments_course(course_id)}) a, const
               LEFT JOIN
               (
                 SELECT assignment_id, SUM(percent_passed > 0) AS num_passed, SUM(percent_passed) AS total_percent
                 FROM
                 (
                   SELECT sc.assignment_id, sc.user_id, SUM(sc.score) / nvp.problem_count AS percent_passed
                   FROM ({students_course(course_id)}) st
                   LEFT JOIN scores sc
                     ON st.user_id = sc.user_id
                   INNER JOIN ({num_visible_problems_course(course_id)}) nvp
                     ON sc.assignment_id = nvp.assignment_id
                   GROUP BY sc.assignment_id, sc.user_id
                 )
               GROUP BY assignment_id
               ) b
                 ON a.assignment_id = b.assignment_id'''
