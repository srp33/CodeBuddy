from BaseUserHandler import *
import datetime as dt

class ViewAtRiskStudentsHandler(BaseUserHandler):
    async def get(self, course_id, assignment_id, exercise_id):
        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
                course_basics = await self.get_course_basics(course_id)
                assignments = await self.get_assignments(course_basics)

                next_prev_exercises = self.content.get_next_prev_exercises(course_id, assignment_id, exercise_id, exercise_statuses)

                format_exercise_details(exercise_details, course_id, assignment_id, user_info, self.content)
                self.render("view_instructor_solution.html", courses=self.courses, assignments=assignments, course_basics=course_basics, assignment_basics=assignment_basics, assignment_details=assignment_details, exercise_basics=exercise_basics, exercise_details=exercise_details, exercise_statuses=exercise_statuses, next_exercise=next_prev_exercises["next"],prev_exercise=next_prev_exercises["previous"], user_code=user_code, user_info=user_info, check_for_restrict_other_assignments=course_details["check_for_restrict_other_assignments"], is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id), is_assistant=await self.is_assistant_for_course(course_id))
            
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())