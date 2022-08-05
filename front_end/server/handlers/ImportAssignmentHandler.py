from BaseUserHandler import *

class ImportAssignmentHandler(BaseUserHandler):
    def get(self, course):
        try:
            self.render("import_assignment.html", courses=self.get_courses(False), assignments=self.content.get_assignments(course, False), assignment_statuses=self.content.get_assignment_statuses(course, self.get_user_id()), course_basics=self.content.get_course_basics(course), is_administrator=self.is_administrator(), is_instructor=self.is_instructor_for_course(course), user_info = self.get_user_info())
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course):
        try:
            course_basics = self.content.get_course_basics(course)

            if not course_basics["exists"]:
                return self.write_output(f"Error: The specified course ID ({course_id}) is invalid.")

            file_text = self.get_body_argument("file_text")
            assignment_dict = json.loads(file_text)

            for x in ["basics", "details", "exercises"]:
                if x not in assignment_dict:
                    return self.write_output(f"Error: The contents of the uploaded file are invalid ({x} is missing at level 1).")

            assignment_basics = assignment_dict["basics"]
            assignment_details = assignment_dict["details"]

            # Make sure assignment with that title doesn't already exist.
            if self.content.has_duplicate_title(self.content.get_assignments(course), None, assignment_basics["title"]):
                return self.write_output("Error: An assignment with that title already exists.")

            for exercise_title in assignment_dict["exercises"]:
                for x in ["basics", "details"]:
                    if x not in assignment_dict:
                        return self.write_output(f"Error: The contents of the uploaded file are invalid ({x} is missing at level 2).")

            assignment_basics["exists"] = False
            assignment_basics["course"] = {"id": course}
            assignment_id = self.content.save_assignment(assignment_basics, assignment_details)
            assignment_basics["id"] = assignment_id

            for exercise_title in assignment_dict["exercises"]:
                exercise_basics = assignment_dict["exercises"][exercise_title]["basics"]
                exercise_details = assignment_dict["exercises"][exercise_title]["details"]

                exercise_basics["exists"] = False
                exercise_basics["assignment"] = assignment_basics
                self.content.save_exercise(exercise_basics, exercise_details)

            self.write_output(str(assignment_id))
        except Exception as inst:
            return self.write_output(f"Error: {traceback.format_exc()}")

    def write_output(self, message):
        self.write(message.encode())
