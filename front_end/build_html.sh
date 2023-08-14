# <copyright_statement>
#   CodeBuddy - A learning management system for computer programming
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

#! /bin/bash

set -e

OUTPUT=$(pwd)/$1

echo "Building HTML files..."

mkdir -p $OUTPUT
rm -f $OUTPUT/*

cd templates

for page_name in home about choose_login_option contact_us devlogin
do
  # cat header.html navbar_top.html navbar_bottom.html container_color.html ${page_name}.html container_bottom.html footer.html > "$OUTPUT/${page_name}.html"
  cat header.html container_color.html ${page_name}.html container_bottom.html footer.html > "$OUTPUT/${page_name}.html"
done

# Dynamic pages

cat test.html > "$OUTPUT/test.html"
cat header.html navbar_top.html navbar_menu.html navbar_bottom.html container_color.html courses.html container_bottom.html footer.html > "$OUTPUT/courses.html"
cat header.html navbar_top.html navbar_menu.html navbar_bottom.html container_color.html available.html container_bottom.html footer.html > "$OUTPUT/available.html"
cat header.html navbar_top.html navbar_menu.html navbar_bottom.html container_color.html manage_admins.html container_bottom.html footer.html > "$OUTPUT/manage_admins.html"
cat header.html navbar_top.html navbar_menu.html navbar_bottom.html container_color.html manage_instructors.html container_bottom.html footer.html > "$OUTPUT/manage_instructors.html"
cat header.html navbar_top.html navbar_menu.html navbar_bottom.html container_color.html manage_assistants.html container_bottom.html footer.html > "$OUTPUT/manage_assistants.html"
cat header.html navbar_top.html navbar_menu.html navbar_bottom.html container_color.html manage_students.html container_bottom.html footer.html > "$OUTPUT/manage_students.html"
cat header.html navbar_top.html navbar_menu.html navbar_bottom.html container_color.html manage_users.html container_bottom.html footer.html > "$OUTPUT/manage_users.html"
cat header.html navbar_top.html navbar_menu.html navbar_bottom.html container_color.html my_profile.html container_bottom.html footer.html > "$OUTPUT/my_profile.html"
cat header.html javascript_container.html navbar_top.html navbar_menu.html navbar_bottom.html container_color.html preferences.html container_bottom.html footer.html > "$OUTPUT/preferences.html"
#cat profile_header.html navbar_top.html navbar_menu.html navbar_bottom.html profile.html profile_help_requests.html profile_bottom.html footer.html > "$OUTPUT/profile_help_requests.html"
#cat profile_header.html navbar_top.html navbar_menu.html navbar_bottom.html profile.html profile_student_help_requests.html profile_bottom.html footer.html > "$OUTPUT/profile_student_help_requests.html"
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_menu.html navbar_bottom.html container_color.html course.html container_bottom.html footer.html > "$OUTPUT/course.html"
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_menu.html navbar_bottom.html container_color.html course_admin.html other_functions.html container_bottom.html footer.html > "$OUTPUT/course_admin.html"
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_menu.html navbar_bottom.html container_color.html edit_course.html container_bottom.html footer.html > "$OUTPUT/edit_course.html"
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html container_color.html assignment.html container_bottom.html footer.html > "$OUTPUT/assignment.html"
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html container_color.html assignment_admin.html other_functions.html container_bottom.html footer.html > "$OUTPUT/assignment_admin.html"
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html container_color.html edit_assignment.html container_bottom.html footer.html > "$OUTPUT/edit_assignment.html"
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_menu.html navbar_bottom.html container_color.html resave_exercises.html container_bottom.html footer.html > "$OUTPUT/resave_exercises.html"
cat header.html javascript_container.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html container_color.html exercise_functions.html exercise.html container_bottom.html footer.html > "$OUTPUT/exercise.html"
cat header.html javascript_container.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html container_color.html edit_exercise.html container_bottom.html footer.html > "$OUTPUT/edit_exercise.html"
cat header.html navbar_top.html navbar_course.html navbar_menu.html navbar_bottom.html container_color.html view_at_risk_students.html container_bottom.html footer.html > "$OUTPUT/view_at_risk_students.html"
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html container_color.html exercise_functions.html view_instructor_solution.html container_bottom.html footer.html > "$OUTPUT/view_instructor_solution.html"
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html container_color.html exercise_functions.html view_peer_solution.html container_bottom.html footer.html > "$OUTPUT/view_peer_solution.html"
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html container_color.html view_assignment_scores.html container_bottom.html footer.html > "$OUTPUT/view_assignment_scores.html"
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_menu.html navbar_bottom.html container_color.html view_student_assignment_scores.html container_bottom.html footer.html > "$OUTPUT/view_student_assignment_scores.html"
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html container_color.html edit_assignment_scores.html container_bottom.html footer.html > "$OUTPUT/edit_assignment_scores.html"
cat header.html javascript_container.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html container_color.html exercise_functions.html student_exercise.html container_bottom.html footer.html > "$OUTPUT/student_exercise.html"
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_menu.html navbar_bottom.html container_color.html view_exercise_scores.html container_bottom.html footer.html > "$OUTPUT/view_exercise_scores.html"
cat header.html navbar_top.html navbar_course.html navbar_menu.html navbar_bottom.html container_color.html help_requests.html container_bottom.html footer.html > "$OUTPUT/help_requests.html"
cat header.html javascript_container.html navbar_top.html navbar_course.html navbar_menu.html navbar_bottom.html view_request.html container_bottom.html footer.html > "$OUTPUT/view_request.html"
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_menu.html navbar_bottom.html container_color.html exercise_submissions.html container_bottom.html footer.html > "$OUTPUT/exercise_submissions.html"
cat header.html navbar_top.html navbar_menu.html navbar_bottom.html container_color.html summarize_logs.html container_bottom.html footer.html > "$OUTPUT/summarize_logs.html"
cat header.html navbar_top.html navbar_menu.html navbar_bottom.html container_color.html delete_user.html container_bottom.html footer.html > "$OUTPUT/delete_user.html"

cat header.html diff_txt.html footer.html > "$OUTPUT/diff_txt.html"
cat header.html diff_jpg.html footer.html > "$OUTPUT/diff_jpg.html"

cat header.html navbar_top.html navbar_bottom.html container_color.html error.html container_bottom.html footer.html > "$OUTPUT/error.html"
cat header.html navbar_top.html navbar_bottom.html container_color.html permissions.html container_bottom.html footer.html > "$OUTPUT/permissions.html"
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_menu.html navbar_bottom.html container_color.html unavailable_exercise.html container_bottom.html footer.html > "$OUTPUT/unavailable_exercise.html"
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_menu.html navbar_bottom.html container_color.html unavailable_assignment.html container_bottom.html footer.html > "$OUTPUT/unavailable_assignment.html"
cat header.html navbar_top.html navbar_course.html navbar_menu.html navbar_bottom.html container_color.html unavailable_course.html container_bottom.html footer.html > "$OUTPUT/unavailable_course.html"

cat spa_header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_exercise.html navbar_menu.html navbar_bottom.html spa.html footer.html > "$OUTPUT/spa.html"

for f in "$OUTPUT"/*.html
do
  python3 ../misc/remove_copyright_statement.py $f "<!--" "-->"
done

echo "Done building HTML files. They are stored in ${OUTPUT}."

cd - &> /dev/null