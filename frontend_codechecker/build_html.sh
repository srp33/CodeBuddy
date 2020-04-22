#! /bin/bash

cat /tmp/header.html /tmp/home.html /tmp/footer.html > /app/home.html
cat /tmp/header.html /tmp/navbar_top.html /tmp/navbar_course.html /tmp/navbar_bottom.html /tmp/course.html /tmp/footer.html > /app/course.html
cat /tmp/header.html /tmp/navbar_top.html /tmp/navbar_course.html /tmp/navbar_bottom.html /tmp/edit_course.html /tmp/footer.html > /app/edit_course.html
cat /tmp/header.html /tmp/navbar_top.html /tmp/navbar_course.html /tmp/navbar_bottom.html /tmp/delete_course.html /tmp/footer.html > /app/delete_course.html
cat /tmp/header.html /tmp/navbar_top.html /tmp/navbar_course.html /tmp/navbar_assignment.html /tmp/navbar_bottom.html /tmp/assignment.html /tmp/footer.html > /app/assignment.html
cat /tmp/header.html /tmp/navbar_top.html /tmp/navbar_course.html /tmp/navbar_assignment.html /tmp/navbar_bottom.html /tmp/edit_assignment.html /tmp/footer.html > /app/edit_assignment.html
cat /tmp/header.html /tmp/navbar_top.html /tmp/navbar_course.html /tmp/navbar_assignment.html /tmp/navbar_bottom.html /tmp/delete_assignment.html /tmp/footer.html > /app/delete_assignment.html
cat /tmp/header.html /tmp/navbar_top.html /tmp/navbar_course.html /tmp/navbar_assignment.html /tmp/navbar_problem.html /tmp/navbar_bottom.html /tmp/problem.html /tmp/footer.html > /app/problem.html
cat /tmp/header.html /tmp/navbar_top.html /tmp/navbar_course.html /tmp/navbar_assignment.html /tmp/navbar_problem.html /tmp/navbar_bottom.html /tmp/edit_problem.html /tmp/footer.html > /app/edit_problem.html
cat /tmp/header.html /tmp/navbar_top.html /tmp/navbar_course.html /tmp/navbar_assignment.html /tmp/navbar_problem.html /tmp/navbar_bottom.html /tmp/delete_problem.html /tmp/footer.html > /app/delete_problem.html

cat /tmp/header.html /tmp/error.html /tmp/footer.html > /app/error.html
