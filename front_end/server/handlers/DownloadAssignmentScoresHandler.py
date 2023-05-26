from BaseUserHandler import *

class DownloadAssignmentScoresHandler(BaseUserHandler):
    def get(self, course, assignment):
        try:
            if self.is_administrator or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                course_basics = self.get_course_basics(course)
                assignment_basics = self.content.get_assignment_basics(course_basics, assignment)

                tsv_text = self.content.create_assignment_scores_text(course_basics, assignment_basics)
                
                self.set_header('Content-type', "text/tab-separated-values")
                self.write(tsv_text)
            else:
                self.write("Permission denied")
        except Exception as inst:
            self.write(traceback.format_exc())

