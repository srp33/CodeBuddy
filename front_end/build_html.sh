#! /bin/bash

cd /tmp

# Dynamic pages

cat header.html navbar_top.html navbar_course.html navbar_bottom.html container_top.html home.html container_bottom.html footer.html > /app/home.html
cat header.html navbar_top.html navbar_bottom.html container_top.html login.html container_bottom.html footer.html > /app/login.html
cat header.html navbar_top.html navbar_course.html navbar_bottom.html container_top.html course.html container_bottom.html footer.html > /app/course.html
cat header.html navbar_top.html navbar_course.html navbar_bottom.html container_top.html course_admin.html container_bottom.html footer.html > /app/course_admin.html
cat header.html navbar_top.html navbar_course.html navbar_bottom.html container_top.html edit_course.html container_bottom.html footer.html > /app/edit_course.html
cat header.html navbar_top.html navbar_course.html navbar_bottom.html container_top.html delete_course.html container_bottom.html footer.html > /app/delete_course.html
cat header.html navbar_top.html navbar_course.html navbar_bottom.html container_top.html delete_course_submissions.html container_bottom.html footer.html > /app/delete_course_submissions.html
cat header.html navbar_top.html navbar_bottom.html container_top.html import_course.html container_bottom.html footer.html > /app/import_course.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_problem.html navbar_bottom.html container_top.html assignment.html container_bottom.html footer.html > /app/assignment.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_problem.html navbar_bottom.html container_top.html assignment_admin.html container_bottom.html footer.html > /app/assignment_admin.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_problem.html navbar_bottom.html container_top.html edit_assignment.html container_bottom.html footer.html > /app/edit_assignment.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_problem.html navbar_bottom.html container_top.html delete_assignment.html container_bottom.html footer.html > /app/delete_assignment.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_problem.html navbar_bottom.html container_top.html delete_assignment_submissions.html container_bottom.html footer.html > /app/delete_assignment_submissions.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_problem.html navbar_bottom.html container_top.html problem.html container_bottom.html footer.html > /app/problem.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_problem.html navbar_bottom.html container_top.html edit_problem.html container_bottom.html footer.html > /app/edit_problem.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_problem.html navbar_bottom.html container_top.html delete_problem.html container_bottom.html footer.html > /app/delete_problem.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_problem.html navbar_bottom.html container_top.html delete_problem_submissions.html container_bottom.html footer.html > /app/delete_problem_submissions.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_problem.html navbar_bottom.html container_top.html view_answer.html container_bottom.html footer.html > /app/view_answer.html
cat header.html navbar_top.html navbar_course.html navbar_bottom.html container_top.html add_admin.html container_bottom.html footer.html > /app/add_admin.html
cat header.html navbar_top.html navbar_course.html navbar_bottom.html container_top.html add_instructor.html container_bottom.html footer.html > /app/add_instructor.html
cat header.html navbar_top.html navbar_course.html navbar_bottom.html container_top.html add_assistant.html container_bottom.html footer.html > /app/add_assistant.html
cat header.html navbar_top.html navbar_course.html navbar_bottom.html container_top.html view_scores.html container_bottom.html footer.html > /app/view_scores.html
cat header.html navbar_top.html navbar_course.html navbar_bottom.html container_top.html student_scores.html container_bottom.html footer.html > /app/student_scores.html
cat header.html navbar_top.html navbar_bottom.html container_top.html summarize_logs.html container_bottom.html footer.html > /app/summarize_logs.html
cat header.html navbar_top.html navbar_bottom.html container_top.html student_problem.html container_bottom.html footer.html > /app/student_problem.html

cat header.html navbar_top.html navbar_bottom.html container_top.html initialize.html container_bottom.html footer.html > /app/initialize.html
cat header.html navbar_top.html navbar_bottom.html container_top.html error.html container_bottom.html footer.html > /app/error.html
cat header.html navbar_top.html navbar_bottom.html container_top.html permissions.html container_bottom.html footer.html > /app/permissions.html

# Static pages

for page_name in about contact_us
do
  cat header.html navbar_top.html navbar_bottom.html container_top.html ${page_name}.html container_bottom.html footer.html > /static/${page_name}.html
done

cd -
