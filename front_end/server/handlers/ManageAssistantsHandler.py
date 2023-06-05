from BaseUserHandler import *

class ManageAssistantsHandler(BaseUserHandler):
    async def get(self, course_id):
        try:
            is_assistant = await self.is_assistant_for_course(course_id)

            if self.is_administrator or await self.is_instructor_for_course(course_id) or is_assistant:
                self.render("manage_assistants.html", course_basics=await self.get_course_basics(course_id), assistants=self.content.get_users_from_role(course_id, "assistant"), user_info=self.user_info, is_administrator=self.is_administrator, is_assistant=is_assistant)
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())