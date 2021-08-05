from helper import *
import traceback
from BaseUserHandler import *
from content import *


settings_dict = load_yaml_dict(read_file("/Settings.yaml"))
content = Content(settings_dict)

class DownloadScoresHandler(BaseUserHandler):
    def get(self, course, assignment):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                csv_text = content.create_scores_text(course, assignment)
                self.set_header('Content-type', "text/csv")
                self.write(csv_text)
            else:
                self.render("permissions.html")
        except Exception as inst:
            self.write(traceback.format_exc())
            #render_error(self, traceback.format_exc())

