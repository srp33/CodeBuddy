from BaseUserHandler import *

class CopyCourseHandler(BaseUserHandler):
    def post(self, course):
        out_dict = {"result": ""}

        try:
            if not self.is_administrator() and not self.is_instructor_for_course(course):
                out_dict["result"] = "You do not have permission to perform this task."
            else:
                new_title = self.get_body_argument("new_title").strip()
                existing_titles = list(map(lambda x: x[1]["title"], self.content.get_courses(False)))

                if new_title in existing_titles:
                    out_dict["result"] = "Error: A course with that title already exists."
                else:
                    self.content.copy_course(course, new_title)
        except Exception as inst:
            out_dict["result"] = traceback.format_exc()

        self.write(json.dumps(out_dict))
