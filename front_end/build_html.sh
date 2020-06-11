#! /bin/bash

cd /tmp

# Dynamic pages

cat header.html navbar_top.html navbar_bottom.html container_top.html home.html container_bottom_home.html container_bottom_all.html footer.html > /app/home.html
cat header.html navbar_top.html navbar_bottom.html container_top.html login.html container_bottom_all.html footer.html > /app/login.html
cat header.html navbar_top.html navbar_course.html navbar_bottom.html container_top.html course.html container_bottom_other.html container_bottom_all.html footer.html > /app/course.html
cat header.html navbar_top.html navbar_course.html navbar_bottom.html container_top.html edit_course.html container_bottom_other.html container_bottom_all.html footer.html > /app/edit_course.html
cat header.html navbar_top.html navbar_course.html navbar_bottom.html container_top.html delete_course.html container_bottom_other.html container_bottom_all.html footer.html > /app/delete_course.html
cat header.html navbar_top.html navbar_bottom.html container_top.html import_course.html container_bottom_other.html container_bottom_all.html footer.html > /app/import_course.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_bottom.html container_top.html assignment.html container_bottom_other.html container_bottom_all.html footer.html > /app/assignment.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_bottom.html container_top.html edit_assignment.html container_bottom_other.html container_bottom_all.html footer.html > /app/edit_assignment.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_bottom.html container_top.html delete_assignment.html container_bottom_other.html container_bottom_all.html footer.html > /app/delete_assignment.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_problem.html navbar_bottom.html container_top.html problem.html container_bottom_other.html container_bottom_all.html footer.html > /app/problem.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_problem.html navbar_bottom.html container_top.html edit_problem.html container_bottom_other.html container_bottom_all.html footer.html > /app/edit_problem.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_problem.html navbar_bottom.html container_top.html delete_problem.html container_bottom_other.html container_bottom_all.html footer.html > /app/delete_problem.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_problem.html navbar_bottom.html container_top.html view_answer.html container_bottom_other.html container_bottom_all.html footer.html > /app/view_answer.html
cat header.html navbar_top.html navbar_course.html navbar_bottom.html container_top.html permissions.html container_bottom_other.html container_bottom_all.html footer.html > /app/permissions.html

cat header.html container_top.html error.html container_bottom_other.html container_bottom_all.html footer.html > /app/error.html

# Static pages

cat header.html navbar_top.html navbar_bottom.html container_top.html about.html container_bottom_all.html footer.html > /static/about.html

cd -
