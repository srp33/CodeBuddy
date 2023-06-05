from BaseUserHandler import *

class RegisterHandler(BaseUserHandler):
    async def get(self, course_id, user_id, passcode):
        result = "Error: No response"

        try:
            course_basics = await self.get_course_basics(course_id)
            course_details = await self.get_course_details(course_id)
            course_title = course_basics["title"]
            course_passcode = course_details["passcode"]

            all_courses = self.content.get_all_courses()
            all_course_ids = [course[0] for course in all_courses]

            if (course_passcode == None or course_passcode == passcode):
                if int(course_id) in all_course_ids:
                    if (self.content.is_user_registered(course_id, user_id)):
                        result = f"Error: You are already registered for {course_title}."
                    else:
                        self.content.register_user_for_course(course_id, user_id)
                        #TODO: Clear cookie for courses
                        result = f"Success"
                else:
                    result = "Error: A course with that ID was not found."
            elif passcode == "":
                result = "Error: Please enter a passcode."
            else:
                result = "Error: Incorrect passcode."
        except Exception as inst:
            result = f"Error: {traceback.format_exc()}"

        self.write(result)