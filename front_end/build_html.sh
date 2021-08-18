#! /bin/bash

cd /tmp

# Simple pages

for page_name in about contact_us devlogin
do
  cat header.html navbar_top.html navbar_bottom.html container_color.html ${page_name}.html container_bottom.html footer_version.html > /app/${page_name}.html
done

# Dynamic pages

cat test.html >/app/test.html
cat header.html navbar_top.html navbar_bottom.html home.html footer_version.html > /app/home.html
cat profile_header.html navbar_top.html navbar_menu.html navbar_bottom.html profile.html profile_courses.html profile_bottom.html footer_version.html > /app/profile_courses.html
cat profile_header.html navbar_top.html navbar_menu.html navbar_bottom.html profile.html consent_forms.html profile_bottom.html footer_version.html > /app/consent_forms.html
cat profile_header.html navbar_top.html navbar_menu.html navbar_bottom.html profile.html profile_personal_info.html profile_bottom.html footer_version.html > /app/profile_personal_info.html
cat profile_header.html navbar_top.html navbar_menu.html navbar_bottom.html profile.html profile_admin.html profile_bottom.html footer_version.html > /app/profile_admin.html
cat profile_header.html navbar_top.html navbar_menu.html navbar_bottom.html profile.html profile_select_course.html profile_bottom.html footer_version.html > /app/profile_select_course.html
cat profile_header.html navbar_top.html navbar_menu.html navbar_bottom.html profile.html profile_instructor.html profile_bottom.html footer_version.html > /app/profile_instructor.html
cat profile_header.html navbar_top.html navbar_menu.html navbar_bottom.html profile.html profile_manage_users.html profile_bottom.html footer_version.html > /app/profile_manage_users.html
cat profile_header.html navbar_top.html navbar_menu.html navbar_bottom.html profile.html profile_help_requests.html profile_bottom.html footer_version.html > /app/profile_help_requests.html
cat profile_header.html navbar_top.html navbar_menu.html navbar_bottom.html profile.html profile_student_help_requests.html profile_bottom.html footer_version.html > /app/profile_student_help_requests.html
cat profile_header.html javascript_container.html navbar_top.html navbar_menu.html navbar_bottom.html profile.html profile_preferences.html profile_bottom.html footer_version.html > /app/profile_preferences.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_menu.html navbar_bottom.html container_color.html course.html container_bottom.html footer_version.html > /app/course.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_menu.html navbar_bottom.html container_color.html course_admin.html container_bottom.html footer_version.html > /app/course_admin.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_menu.html navbar_bottom.html container_color.html edit_course.html container_bottom.html footer_version.html > /app/edit_course.html
cat header.html navbar_top.html navbar_course.html navbar_menu.html navbar_bottom.html container_color.html delete_course.html container_bottom.html footer_version.html > /app/delete_course.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html container_color.html assignment.html container_bottom.html footer_version.html > /app/assignment.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html container_color.html assignment_admin.html container_bottom.html footer_version.html > /app/assignment_admin.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html container_color.html edit_assignment.html container_bottom.html footer_version.html > /app/edit_assignment.html
cat header.html javascript_container.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html container_color.html exercise.html exercise_shared.html container_bottom.html footer_version.html > /app/exercise.html
cat header.html javascript_container.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html container_color.html edit_exercise.html container_bottom.html footer_version.html > /app/edit_exercise.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html container_color.html view_answer.html container_bottom.html footer_version.html > /app/view_answer.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html container_color.html view_scores.html container_bottom.html footer_version.html > /app/view_scores.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html container_color.html edit_scores.html container_bottom.html footer_version.html > /app/edit_scores.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html container_color.html student_scores.html container_bottom.html footer_version.html > /app/student_scores.html
cat header.html javascript_container.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html container_color.html student_exercise.html exercise_shared.html student_exercise_back_button.html container_bottom.html footer_version.html > /app/student_exercise.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_menu.html navbar_bottom.html container_color.html exercise_scores.html container_bottom.html footer_version.html > /app/exercise_scores.html
cat header.html navbar_top.html navbar_course.html navbar_menu.html navbar_bottom.html container_color.html help_requests.html container_bottom.html footer_version.html > /app/help_requests.html
cat header.html javascript_container.html navbar_top.html navbar_course.html navbar_menu.html navbar_bottom.html view_request.html container_bottom.html footer_version.html > /app/view_request.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_menu.html navbar_bottom.html container_color.html exercise_submissions.html container_bottom.html footer_version.html > /app/exercise_submissions.html
cat header.html navbar_top.html navbar_menu.html navbar_bottom.html container_color.html summarize_logs.html container_bottom.html footer_version.html > /app/summarize_logs.html

cat header.html navbar_top.html navbar_bottom.html container_color.html error.html container_bottom.html footer_version.html > /app/error.html
cat header.html navbar_top.html navbar_bottom.html container_color.html permissions.html container_bottom.html footer_version.html > /app/permissions.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_menu.html navbar_bottom.html container_color.html unavailable_assignment.html container_bottom.html footer_version.html > /app/unavailable_assignment.html
cat header.html navbar_top.html navbar_menu.html navbar_bottom.html container_color.html timer_error.html container_bottom.html footer_version.html > /app/timer_error.html

cd -
