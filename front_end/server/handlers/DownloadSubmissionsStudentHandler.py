# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class DownloadSubmissionsStudentHandler(BaseUserHandler):
    async def get(self, course_id):
        try:
            course_details = await self.get_course_details(course_id)

            if course_details["allow_students_download_submissions"]:
                html = await self.format(course_id, self.content.get_submissions_student(course_id, self.get_current_user()))

                self.write(html)
                self.set_header('Content-type', "text/html")
            else:
                render_error(self, "You do not have permission to download your submissions.")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    async def format(self, course_id, submissions):
        course_basics = await self.get_course_basics(course_id)
        html = "<html><body>"
        html += '''<head>
                       <style>
                           @import url('https://fonts.googleapis.com/css2?family=Roboto&family=Source+Code+Pro&display=swap');
                           body {
                               font-family: 'Roboto', sans-serif;
                               font-size: 16px;
                               width: 95%;
                               padding: 15;
                           }
                           pre {
                               font-family: 'Source Code Pro', monospace;
                               width: 95%;
                               padding: 5;
                               margin: 0;
                               overflow: auto;
                               overflow-y: hidden;
                               font-size: 14px;
                               background: #efefef;
                               border: 1px solid #777;
                           }
                       </style>
                   </head>'''

        if len(submissions) == 0:
            html += f"<p>You have not yet made any submissions for this course.</p>"
        else:
            html += f"<h1>Submissions by {self.get_current_user()} for {course_basics['title']}</h1>"
            html += f"<p>This document contains the latest <i>passing</i> submission for each exercise. Timed assignments are excluded. In some cases, exercises do <i>not</i> require you to write code; the submissions for these exercises are excluded.</p>"

            assignments_started = []

            for submission in submissions:
                if submission["assignment_title"] not in assignments_started:
                    assignments_started.append(submission["assignment_title"])
                    html += f"<h4>{submission['assignment_title']}</h4>"
                    html += f"{convert_markdown_to_html(submission['assignment_introduction'])}"

                html += f"<h4>{submission['exercise_title']}</h4>"
                html += f"{convert_markdown_to_html(submission['exercise_instructions'])}"

                html += f"<p><i>Your solution:</i></p>"
                html += f"<pre>{submission['code']}</pre>"

        html += f"<p><i>This file was generated on {get_current_datetime()} (GMT).</i></p>"
        return html + "</body></html>"