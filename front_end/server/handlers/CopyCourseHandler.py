from BaseUserHandler import *

class CopyCourseHandler(BaseUserHandler):
    async def post(self, course_id):
        result = ""

        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id):
                new_title = self.get_body_argument("new_title").strip()
                existing_titles = list(map(lambda x: x[1]["title"], self.courses))

                if new_title in existing_titles:
                    result = "Error: A course with that title already exists."
                else:
                    course_basics = await self.get_course_basics(course_id)
                    await self.content.copy_course(course_basics, new_title)
            else:
                result = "You do not have permission to perform this task."
        except Exception as inst:
            result = f"Error: {traceback.format_exc()}"

        self.write(result)