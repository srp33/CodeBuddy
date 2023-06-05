from BaseUserHandler import *

class HelpRequestsHandler(BaseUserHandler):
    async def get(self, course_id):
        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
                course_basics = await self.get_course_basics(course_id)

                self.render("help_requests.html", courses=self.courses, course_basics=course_basics, assignments=await self.get_assignments(course_basics), help_requests=self.content.get_help_requests(course_id), user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id), is_assistant=await self.is_assistant_for_course(course_id))
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())