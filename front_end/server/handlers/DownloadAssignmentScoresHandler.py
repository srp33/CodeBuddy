from BaseUserHandler import *

class DownloadAssignmentScoresHandler(BaseUserHandler):
    def get(self, course, assignment):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                tsv_text = self.content.create_assignment_scores_text(course, assignment)
                self.set_header('Content-type', "text/tab-separated-values")
                self.write(tsv_text)
            else:
                self.write("Permission denied")
        except Exception as inst:
            self.write(traceback.format_exc())

