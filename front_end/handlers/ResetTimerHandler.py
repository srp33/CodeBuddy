import sys
sys.path.append("..")
from StaticFileHandler import *
import traceback
from BaseUserHandler import *
from content import *

settings_dict = load_yaml_dict(read_file("/Settings.yaml"))
content = Content(settings_dict)

class ResetTimerHandler(BaseUserHandler):
    async def post(self, course, assignment, user):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                content.reset_user_assignment_start_timer(course, assignment, user)
            else:
                self.render("permissions.html")

        except Exception as inst:
            self.write(traceback.format_exc())

