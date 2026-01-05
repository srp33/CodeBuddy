# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class DownloadAssignmentScoresHandler(BaseUserHandler):
    async def get(self, course_id, assignment_id):
        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
                course_basics = await self.get_course_basics(course_id)
                assignment_basics = self.content.get_assignment_basics(course_basics, assignment_id)

                scores, total_times_pair_programmed = self.content.get_assignment_scores(course_basics, assignment_basics)

                out_file_prefix = re.sub(r"\W", "_", assignment_basics['title'])

                self.set_header("Content-Disposition", f"attachment; filename=Scores__{out_file_prefix}__{get_formatted_datetime()}.tsv")
                self.set_header('Content-type', "text/tab-separated-values")

                self.write("Course\tAssignment\tStudent_ID\tNum_Completed\tScore\tLast_Submission\tNum_Times_Pair_Programmed\n")

                for student in scores:
                    self.write(f"{course_basics['title']}\t{assignment_basics['title']}\t{student[0]}\t{student[1]['num_completed']}\t{student[1]['score']}\t{student[1]['last_submission_timestamp']}\t{student[1]['num_times_pair_programmed']}\n")
            else:
                self.write("Permission denied")
        except Exception as inst:
            self.write(traceback.format_exc())