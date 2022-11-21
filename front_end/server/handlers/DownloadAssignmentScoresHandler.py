from BaseUserHandler import *

class DownloadAssignmentScoresHandler(BaseUserHandler):
    def get(self, course, assignment):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                csv_text = self.content.create_assignment_scores_text(course, assignment)
                self.set_header('Content-type', "text/csv")
                self.write(csv_text)
            else:
                self.render("permissions.html")
        except Exception as inst:
            print(traceback.format_exc())
            self.write(traceback.format_exc())

