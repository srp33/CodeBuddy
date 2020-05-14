#! /bin/bash

cd /tmp

cat header.html navbar_top.html navbar_bottom.html container_top.html home.html container_bottom.html footer.html > /app/home.html
cat header.html navbar_top.html navbar_course.html navbar_bottom.html container_top.html course.html container_bottom.html footer.html > /app/course.html
cat header.html navbar_top.html navbar_course.html navbar_bottom.html container_top.html edit_course.html container_bottom.html footer.html > /app/edit_course.html
cat header.html navbar_top.html navbar_course.html navbar_bottom.html container_top.html delete_course.html container_bottom.html footer.html > /app/delete_course.html
cat header.html navbar_top.html navbar_bottom.html container_top.html import_course.html container_bottom.html footer.html > /app/import_course.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_bottom.html container_top.html assignment.html container_bottom.html footer.html > /app/assignment.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_bottom.html container_top.html edit_assignment.html container_bottom.html footer.html > /app/edit_assignment.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_bottom.html container_top.html delete_assignment.html container_bottom.html footer.html > /app/delete_assignment.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_problem.html navbar_bottom.html container_top.html demo_problem.html container_bottom.html footer.html > /app/problem.html
#cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_problem.html navbar_bottom.html container_top.html problem.html container_bottom.html footer.html > /app/problem.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_problem.html navbar_bottom.html container_top.html edit_problem.html container_bottom.html footer.html > /app/edit_problem.html
cat header.html navbar_top.html navbar_course.html navbar_assignment.html navbar_problem.html navbar_bottom.html container_top.html delete_problem.html container_bottom.html footer.html > /app/delete_problem.html

cat header.html container_top.html error.html container_bottom.html footer.html > /app/error.html

cd -
