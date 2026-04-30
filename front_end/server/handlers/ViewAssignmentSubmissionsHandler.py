# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class ViewAssignmentSubmissionsHandler(BaseUserHandler):
    async def get(self, course_id, assignment_id):
        try:
            assignment_details = await self.get_assignment_details(await self.get_course_basics(course_id), assignment_id, True)

            if assignment_details["allow_students_view_submissions"]:
                submissions = self.content.get_submissions_student_for_assignment(course_id, assignment_id, self.get_current_user())
                html = await self.format(course_id, assignment_id, submissions)
                self.set_header('Content-type', "text/html")
                self.write(html)
            else:
                render_error(self, "You do not have permission to view your submissions for this assignment.")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    async def format(self, course_id, assignment_id, submissions):
        course_basics = await self.get_course_basics(course_id)
        assignment_basics = self.content.get_assignment_basics(course_basics, assignment_id)

        html = "<html>"
        html += '''<head>
                       <style>
                           @import url('https://fonts.googleapis.com/css2?family=Roboto&family=Source+Code+Pro&display=swap');
                           body {
                               font-family: 'Roboto', sans-serif;
                               font-size: 16px;
                               line-height: 1.5;
                               max-width: 900px;
                               margin: 0 auto;
                               padding: 24px 20px 40px;
                               color: #222;
                               background: #fafafa;
                           }
                           .doc-header {
                               margin-bottom: 28px;
                               padding-bottom: 20px;
                               border-bottom: 2px solid #ccc;
                           }
                           .doc-header h1 {
                               font-size: 1.45rem;
                               font-weight: 600;
                               margin: 0 0 10px 0;
                               line-height: 1.35;
                           }
                           .doc-header .doc-meta {
                               margin: 0;
                               color: #444;
                               font-size: 0.95rem;
                           }
                           .doc-intro {
                               margin: 0 0 24px;
                               color: #444;
                               font-size: 0.95rem;
                           }
                           .exercise-section {
                               background: #fff;
                               border: 1px solid #ddd;
                               border-radius: 6px;
                               border-left: 4px solid #5a7fa3;
                               padding: 20px 22px 22px;
                               margin-bottom: 24px;
                               box-shadow: 0 1px 2px rgba(0,0,0,0.04);
                           }
                           .exercise-section:last-of-type {
                               margin-bottom: 16px;
                           }
                           .exercise-title {
                               font-size: 1.15rem;
                               font-weight: 600;
                               margin: 0 0 14px 0;
                               padding-bottom: 10px;
                               border-bottom: 1px solid #e8e8e8;
                               color: #1a1a1a;
                           }
                           .instructions {
                               margin-bottom: 18px;
                           }
                           .instructions p:last-child { margin-bottom: 0; }
                           .part-label {
                               font-size: 0.9rem;
                               font-weight: 600;
                               color: #555;
                               margin: 0 0 8px 0;
                           }
                           .submission-body ul {
                               margin: 0 0 0 1.2em;
                               padding: 0;
                           }
                           .submission-body li {
                               margin-bottom: 0.45em;
                           }
                           pre {
                               font-family: 'Source Code Pro', monospace;
                               width: 100%;
                               box-sizing: border-box;
                               padding: 14px 16px;
                               margin: 0;
                               overflow: auto;
                               font-size: 14px;
                               line-height: 1.45;
                               background: #f3f4f6;
                               border: 1px solid #c5c9d0;
                               border-radius: 4px;
                           }
                           .doc-footer {
                               margin-top: 28px;
                               padding-top: 16px;
                               border-top: 1px solid #ccc;
                               font-size: 0.9rem;
                               color: #666;
                           }
                       </style>
                   </head>'''
        html += "<body>"

        if len(submissions) == 0:
            html += f"<p>You have not yet made any passing submissions for this assignment.</p>"
        else:
            html += '<header class="doc-header">'
            html += f'<h1>Submissions by {self.get_current_user()}</h1>'
            html += f'<p class="doc-meta"><strong>{course_basics["title"]}</strong> &mdash; <strong>{assignment_basics["title"]}</strong></p>'
            html += "</header>"
            html += "<p class=\"doc-intro\">Each exercise below is shown in its own section. For programming exercises, your latest <i>passing</i> submission is shown. For multiple-choice exercises, your most recent submission is shown.</p>"

            for submission in submissions:
                html += '<section class="exercise-section">'
                html += f'<h2 class="exercise-title">{submission["exercise_title"]}</h2>'
                html += f'<div class="instructions">{convert_markdown_to_html(submission["exercise_instructions"])}</div>'
                html += '<div class="submission-body">'

                if submission["back_end"] == "multiple_choice":
                    html += '<p class="part-label">Answer options</p>'
                    html += "<ul>"
                    solutions = json.loads(submission["solution_code"])
                    options = sorted(solutions.keys())
                    selected = submission["code"]
                    for option in options:
                        labels = []
                        if option == selected:
                            labels.append("your answer")
                        if solutions[option]:
                            labels.append("correct answer")
                        suffix = f" <em>({', '.join(labels)})</em>" if labels else ""
                        html += f"<li>{convert_markdown_to_html(option)}{suffix}</li>"
                    html += "</ul>"
                else:
                    html += '<p class="part-label">Your solution</p>'
                    html += f"<pre>{submission['code']}</pre>"

                html += "</div></section>"

        html += f'<footer class="doc-footer"><p style="margin:0;"><i>This document was generated on {get_current_datetime()} (GMT).</i></p></footer>'
        html += "</body></html>"
        return html
