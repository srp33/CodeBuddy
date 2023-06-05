from BaseUserHandler import *

class DownloadAssignmentScoresHandler(BaseUserHandler):
    async def get(self, course_id, assignment_id):
        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
                course_basics = await self.get_course_basics(course_id)
                assignment_basics = self.content.get_assignment_basics(course_basics, assignment_id)

                tsv_text = self.content.create_assignment_scores_text(course_basics, assignment_basics)
                
                self.set_header('Content-type', "text/tab-separated-values")
                self.write(tsv_text)
            else:
                self.write("Permission denied")
        except Exception as inst:
            self.write(traceback.format_exc())