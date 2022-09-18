from BaseUserHandler import *

class CopyCourseHandler(BaseUserHandler):
    def post(self, course):
        result = ""

        try:
            if self.is_administrator() or self.is_instructor_for_course(course):
                new_title = self.get_body_argument("new_title").strip()
                existing_titles = list(map(lambda x: x[1]["title"], self.content.get_courses(False)))

                if new_title in existing_titles:
                    result = "Error: A course with that title already exists."
                else:
                    self.content.copy_course(course, new_title)
            else:
                result = "You do not have permission to perform this task."
        except Exception as inst:
            result = f"Error: {traceback.format_exc()}"

        self.write(result)
