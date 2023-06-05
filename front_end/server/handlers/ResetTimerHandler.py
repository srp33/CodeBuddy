from BaseUserHandler import *

class ResetTimerHandler(BaseUserHandler):
    async def post(self, course_id, assignment_id, user_id):
        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
                self.content.reset_user_assignment_start_timer(course_id, assignment_id, user_id)
            else:
                self.render("permissions.html")

        except Exception as inst:
            self.write(traceback.format_exc())