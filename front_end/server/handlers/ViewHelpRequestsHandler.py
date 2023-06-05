from BaseUserHandler import *

class ViewHelpRequestsHandler(BaseUserHandler):
    async def get(self, course_id, assignment_id, exercise_id, student_id):
        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
                course_basics = await self.get_course_basics(course_id)
                assignment_basics = await self.get_assignment_basics(course_basics, assignment_id)
                exercise_basics = await self.get_exercise_basics(course_basics, assignment_basics, exercise_id)

                self.render("view_request.html", courses=self.courses, course_basics=course_basics, assignments=await self.get_assignments(course_basics), assignment_basics=assignment_basics, exercise_basics=exercise_basics, exercise_details=await self.get_exercise_details(course_basics, assignment_basics, exercise_id), help_request=self.content.get_help_request(course_id, assignment_id, exercise_id, student_id), exercise_help_requests=self.content.get_exercise_help_requests(course_id, assignment_id, exercise_id, student_id), similar_requests=self.content.compare_help_requests(course_id, assignment_id, exercise_id, student_id), result=None, user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id), is_assistant=await self.is_assistant_for_course(course_id))
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    async def post(self, course_id, assignment_id, exercise_id, student_id):
        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
                suggestion = self.get_body_argument("suggestion")
                more_info_needed = self.get_argument("more_info_needed", None) == "More info needed"
                user_id = self.get_current_user()

                if await self.is_assistant_for_course(course_id):
                    self.content.save_help_request_suggestion(course_id, assignment_id, exercise_id, student_id, suggestion, 0, user_id, None, more_info_needed)
                    result = "Success: suggestion submitted for approval"
                else:
                    help_request = self.content.get_help_request(course_id, assignment_id, exercise_id, student_id)
                    if help_request["suggester_id"]:
                        suggester_id = help_request["suggester_id"]
                    else:
                        suggester_id = user_id
                    self.content.save_help_request_suggestion(course_id, assignment_id, exercise_id, student_id, suggestion, 1, suggester_id, user_id, more_info_needed)
                    result = "Success: suggestion saved"

                course_basics = await self.get_course_basics(course_id)
                assignment_basics = await self.get_assignment_basics(course_basics, assignment_id)
                exercise_basics = await self.get_exercise_basics(course_basics, assignment_basics, exercise_id)

                self.render("view_request.html", courses=self.courses, course_basics=course_basics, assignments=await self.get_assignments(course_basics), assignment_basics=assignment_basics, exercise_basics=exercise_basics, exercise_details=await self.get_exercise_details(course_id, assignment_id, exercise_id), help_request=self.content.get_help_request(course_id, assignment_id, exercise_id, student_id), exercise_help_requests=self.content.get_exercise_help_requests(course_id, assignment_id, exercise_id, student_id), similar_requests=self.content.compare_help_requests(course_id, assignment_id, exercise_id, student_id), result=result, user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id), is_assistant=await self.is_assistant_for_course(course_id))
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())