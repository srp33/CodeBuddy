#! /bin/bash

cd /tmp

# Simple pages

for page_name in about contact_us devlogin home
do
  cat header.html navbar_top.html navbar_bottom.html container_top.html ${page_name}.html container_bottom.html footer.html > /app/${page_name}.html
done

# Dynamic pages

cat profile_header.html navbar_top.html navbar_menu.html navbar_bottom.html profile.html profile_courses.html profile_bottom.html footer.html > /app/profile_courses.html
cat profile_header.html navbar_top.html navbar_menu.html navbar_bottom.html profile.html profile_personal_info.html profile_bottom.html footer.html > /app/profile_personal_info.html
cat profile_header.html navbar_top.html navbar_menu.html navbar_bottom.html profile.html profile_admin.html profile_bottom.html footer.html > /app/profile_admin.html
cat profile_header.html navbar_top.html navbar_menu.html navbar_bottom.html profile.html profile_select_course.html profile_bottom.html footer.html > /app/profile_select_course.html
cat profile_header.html navbar_top.html navbar_menu.html navbar_bottom.html profile.html profile_instructor.html profile_bottom.html footer.html > /app/profile_instructor.html
cat profile_header.html navbar_top.html navbar_menu.html navbar_bottom.html profile.html profile_manage_users.html profile_bottom.html footer.html > /app/profile_manage_users.html
cat profile_header.html navbar_top.html navbar_menu.html navbar_bottom.html profile.html profile_preferences.html profile_bottom.html footer.html > /app/profile_preferences.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_menu.html navbar_bottom.html container_top.html course.html container_bottom.html footer.html > /app/course.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_menu.html navbar_bottom.html container_top.html course_admin.html container_bottom.html footer.html > /app/course_admin.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_menu.html navbar_bottom.html container_top.html edit_course.html container_bottom.html footer.html > /app/edit_course.html
cat header.html navbar_top.html navbar_course.html navbar_menu.html navbar_bottom.html container_top.html delete_course.html container_bottom.html footer.html > /app/delete_course.html
cat header.html navbar_top.html navbar_course.html navbar_menu.html navbar_bottom.html container_top.html delete_course_submissions.html container_bottom.html footer.html > /app/delete_course_submissions.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_problem.html navbar_menu.html navbar_bottom.html container_top.html assignment.html container_bottom.html footer.html > /app/assignment.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_problem.html navbar_menu.html navbar_bottom.html container_top.html assignment_admin.html container_bottom.html footer.html > /app/assignment_admin.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_problem.html navbar_menu.html navbar_bottom.html container_top.html edit_assignment.html container_bottom.html footer.html > /app/edit_assignment.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_menu.html navbar_bottom.html container_top.html delete_assignment_submissions.html container_bottom.html footer.html > /app/delete_assignment_submissions.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_problem.html navbar_menu.html navbar_bottom.html container_top.html problem.html problem_shared.html container_bottom.html footer.html > /app/problem.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_problem.html navbar_menu.html navbar_bottom.html container_top.html edit_problem.html container_bottom.html footer.html > /app/edit_problem.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_problem.html navbar_menu.html navbar_bottom.html container_top.html delete_problem_submissions.html container_bottom.html footer.html > /app/delete_problem_submissions.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_problem.html navbar_menu.html navbar_bottom.html container_top.html view_answer.html container_bottom.html footer.html > /app/view_answer.html
cat header.html navbar_top.html navbar_course.html navbar_menu.html navbar_bottom.html container_top.html add_instructor.html container_bottom.html footer.html > /app/add_instructor.html
cat header.html navbar_top.html navbar_course.html navbar_menu.html navbar_bottom.html container_top.html remove_instructor.html container_bottom.html footer.html > /app/remove_instructor.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_problem.html navbar_menu.html navbar_bottom.html container_top.html view_scores.html container_bottom.html footer.html > /app/view_scores.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_problem.html navbar_menu.html navbar_bottom.html container_top.html edit_scores.html container_bottom.html footer.html > /app/edit_scores.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_problem.html navbar_menu.html navbar_bottom.html container_top.html student_scores.html container_bottom.html footer.html > /app/student_scores.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_problem.html navbar_menu.html navbar_bottom.html container_top.html student_problem.html problem_shared.html student_problem_back_button.html container_bottom.html footer.html > /app/student_problem.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_menu.html navbar_bottom.html container_top.html problem_scores.html container_bottom.html footer.html > /app/problem_scores.html
cat header.html navbar_top.html navbar_menu.html navbar_bottom.html container_top.html summarize_logs.html container_bottom.html footer.html > /app/summarize_logs.html
cat header.html navbar_top.html navbar_menu.html navbar_bottom.html container_top.html move_problem.html container_bottom.html footer.html > /app/move_problem.html
cat header.html navbar_top.html navbar_menu.html navbar_bottom.html container_top.html copy_assignment.html container_bottom.html footer.html > /app/copy_assignment.html

cat header.html navbar_top.html navbar_bottom.html container_top.html error.html container_bottom.html footer.html > /app/error.html
cat header.html navbar_top.html navbar_bottom.html container_top.html permissions.html container_bottom.html footer.html > /app/permissions.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_menu.html navbar_bottom.html container_top.html unavailable_assignment.html container_bottom.html footer.html > /app/unavailable_assignment.html
cat header.html navbar_top.html navbar_bottom.html container_top.html timer_error.html container_bottom.html footer.html > /app/timer_error.html

rm *.html

cd -
