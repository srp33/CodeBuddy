#! /bin/bash

# Simple pages
OUTPUT="/app"
if [[ $1 != "" ]]; then
  #OUTPUT=$(realpath $1)
  OUTPUT=$(pwd)/$1
fi

mkdir -p $OUTPUT
rm -f $OUTPUT/*

cd templates

for page_name in about contact_us devlogin
do
  cat header.html navbar_top.html navbar_bottom.html container_color.html ${page_name}.html container_bottom.html footer.html > "$OUTPUT/${page_name}.html"
done

# Dynamic pages

cat test.html > "$OUTPUT/test.html"
cat header.html navbar_top.html navbar_bottom.html home.html footer.html > "$OUTPUT/home.html"
cat profile_header.html navbar_top.html navbar_menu.html navbar_bottom.html profile.html profile_courses.html profile_bottom.html footer.html > "$OUTPUT/profile_courses.html"
cat profile_header.html navbar_top.html navbar_menu.html navbar_bottom.html profile.html consent_forms.html profile_bottom.html footer.html > "$OUTPUT/consent_forms.html"
cat profile_header.html navbar_top.html navbar_menu.html navbar_bottom.html profile.html profile_personal_info.html profile_bottom.html footer.html > "$OUTPUT/profile_personal_info.html"
cat profile_header.html navbar_top.html navbar_menu.html navbar_bottom.html profile.html profile_admin.html profile_bottom.html footer.html > "$OUTPUT/profile_admin.html"
cat profile_header.html navbar_top.html navbar_menu.html navbar_bottom.html profile.html profile_instructor_select_course.html profile_bottom.html footer.html > "$OUTPUT/profile_instructor_select_course.html"
cat profile_header.html navbar_top.html navbar_menu.html navbar_bottom.html profile.html profile_instructor.html profile_bottom.html footer.html > "$OUTPUT/profile_instructor.html"
cat profile_header.html navbar_top.html navbar_menu.html navbar_bottom.html profile.html profile_manage_users.html profile_bottom.html footer.html > "$OUTPUT/profile_manage_users.html"
cat profile_header.html navbar_top.html navbar_menu.html navbar_bottom.html profile.html profile_help_requests.html profile_bottom.html footer.html > "$OUTPUT/profile_help_requests.html"
cat profile_header.html navbar_top.html navbar_menu.html navbar_bottom.html profile.html profile_student_help_requests.html profile_bottom.html footer.html > "$OUTPUT/profile_student_help_requests.html"
cat profile_header.html javascript_container.html navbar_top.html navbar_menu.html navbar_bottom.html profile.html profile_preferences.html profile_bottom.html footer.html > "$OUTPUT/profile_preferences.html"
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_menu.html navbar_bottom.html container_color.html course.html container_bottom.html footer.html > "$OUTPUT/course.html"
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_menu.html navbar_bottom.html container_color.html view_pp.html container_bottom.html footer.html > "$OUTPUT/view_pp.html"
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_menu.html navbar_bottom.html container_color.html course_admin.html container_bottom.html footer.html > "$OUTPUT/course_admin.html"
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_menu.html navbar_bottom.html container_color.html edit_course.html container_bottom.html footer.html > "$OUTPUT/edit_course.html"
cat header.html navbar_top.html navbar_course.html navbar_menu.html navbar_bottom.html container_color.html delete_course.html container_bottom.html footer.html > "$OUTPUT/delete_course.html"
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html container_color.html assignment.html container_bottom.html footer.html > "$OUTPUT/assignment.html"
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html container_color.html assignment_admin.html container_bottom.html footer.html > "$OUTPUT/assignment_admin.html"
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html container_color.html edit_assignment.html container_bottom.html footer.html > "$OUTPUT/edit_assignment.html"
cat header.html navbar_top.html navbar_course.html navbar_menu.html navbar_bottom.html container_color.html import_assignment.html container_bottom.html footer.html > "$OUTPUT/import_assignment.html"
cat header.html javascript_container.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html container_color.html exercise_functions.html exercise.html container_bottom.html footer.html > "$OUTPUT/exercise.html"
cat header.html javascript_container.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html container_color.html edit_exercise.html container_bottom.html footer.html > "$OUTPUT/edit_exercise.html"
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html container_color.html view_instructor_solution.html container_bottom.html footer.html > "$OUTPUT/view_instructor_solution.html"
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html container_color.html view_peer_solution.html container_bottom.html footer.html > "$OUTPUT/view_peer_solution.html"
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html container_color.html view_assignment_scores.html container_bottom.html footer.html > "$OUTPUT/view_assignment_scores.html"
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html container_color.html edit_assignment_scores.html container_bottom.html footer.html > "$OUTPUT/edit_assignment_scores.html"
cat header.html javascript_container.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html container_color.html exercise_functions.html student_exercise.html container_bottom.html footer.html > "$OUTPUT/student_exercise.html"
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_menu.html navbar_bottom.html container_color.html view_exercise_scores.html container_bottom.html footer.html > "$OUTPUT/view_exercise_scores.html"
cat header.html navbar_top.html navbar_course.html navbar_menu.html navbar_bottom.html container_color.html help_requests.html container_bottom.html footer.html > "$OUTPUT/help_requests.html"
cat header.html javascript_container.html navbar_top.html navbar_course.html navbar_menu.html navbar_bottom.html view_request.html container_bottom.html footer.html > "$OUTPUT/view_request.html"
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_menu.html navbar_bottom.html container_color.html exercise_submissions.html container_bottom.html footer.html > "$OUTPUT/exercise_submissions.html"
cat header.html navbar_top.html navbar_menu.html navbar_bottom.html container_color.html summarize_logs.html container_bottom.html footer.html > "$OUTPUT/summarize_logs.html"

cat header.html navbar_top.html navbar_bottom.html container_color.html error.html container_bottom.html footer.html > "$OUTPUT/error.html"
cat header.html navbar_top.html navbar_bottom.html container_color.html permissions.html container_bottom.html footer.html > "$OUTPUT/permissions.html"
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_menu.html navbar_bottom.html container_color.html unavailable_assignment.html container_bottom.html footer.html > "$OUTPUT/unavailable_assignment.html"
cat header.html navbar_top.html navbar_menu.html navbar_bottom.html container_color.html timer_error.html container_bottom.html footer.html > "$OUTPUT/timer_error.html"

cat spa_header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html spa.html footer.html > "$OUTPUT/spa.html"

cd - &> /dev/null
