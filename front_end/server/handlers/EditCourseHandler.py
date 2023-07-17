from BaseUserHandler import *
import datetime as dt

class EditCourseHandler(BaseUserHandler):
    async def get(self, course_id):
        try:
            course_basics = await self.get_course_basics(course_id)
            course_details = await self.get_course_details(course_id)

            if self.is_administrator or await self.is_instructor_for_course(course_id):
                self.render("edit_course.html", courses=self.courses, assignments=self.content.get_assignments(course_basics), course_basics=course_basics, course_details=course_details, result=None, user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id))
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    async def post(self, course_id):
        try:
            if not self.is_administrator and not await self.is_instructor_for_course(course_id):
                self.render("permissions.html")
                return

            course_basics = await self.get_course_basics(course_id)
            course_details = await self.get_course_details(course_id)

            course_basics["title"] = self.get_body_argument("title").strip()
            course_basics["visible"] = self.get_body_argument("is_visible") == "Yes"
            course_details["introduction"] = self.get_body_argument("introduction").strip()
            course_details["passcode"] = self.get_body_argument("passcode").strip()

            if course_details["passcode"] == "":
                course_details["passcode"] = None

            course_details["allow_students_download_submissions"] = self.get_body_argument("allow_students_download_submissions") == "Yes"

            virtual_assistant_config = self.get_body_argument("virtual_assistant_config")
            if virtual_assistant_config.strip() == "":
                virtual_assistant_config = None
            course_details["virtual_assistant_config"] = virtual_assistant_config

            result = "Success: Course information saved!"

            if course_basics["title"] == "" or course_details["introduction"] == "":
                result = "Error: Missing title or introduction."
            else:
                if self.content.has_duplicate_title(self.courses, course_basics["id"], course_basics["title"]):
                    result = "Error: A course with that title already exists."
                else:
                    #if re.search(r"[^\w ]", title):
                    #    result = "Error: The title can only contain alphanumeric characters and spaces."
                    #else:
                    if len(course_basics["title"]) > 100:
                        result = "Error: The title cannot exceed 100 characters."
                    else:
                        vb_dict = {}
                        try:
                            vb_dict = load_yaml_dict(virtual_assistant_config)
                        except:
                            pass

                        if type(vb_dict) is dict and "api_key" in vb_dict and "model" in vb_dict and "temperature" in vb_dict and "timeout" in vb_dict and "max_per_exercise" in vb_dict and type(vb_dict["max_per_exercise"]) is int:
                            #self.content.specify_course_basics(course_basics, course_basics["title"], course_basics["visible"])
                            self.content.specify_course_details(course_details, course_details["introduction"], course_details["passcode"], course_details["allow_students_download_submissions"], course_details["virtual_assistant_config"], None, dt.datetime.utcnow())

                            course_id = self.content.save_course(course_basics, course_details)
                        else:
                            result = "Error: The Virtual Assistant configuration is invalid."

            self.render("edit_course.html", courses=self.courses, assignments=self.content.get_assignments(course_basics), course_basics=course_basics, course_details=course_details, result=result, user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id), is_assistant=await self.is_assistant_for_course(course_id))
        except Exception as inst:
            render_error(self, traceback.format_exc())