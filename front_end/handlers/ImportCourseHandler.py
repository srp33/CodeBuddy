import sys
sys.path.append("..")
from app.helper import *
from app.content import *
import traceback
from BaseUserHandler import *
class ImportCourseHandler(BaseUserHandler):
    def post(self):
        try:
            if not self.is_administrator():
                self.render("permissions.html")
                return

            result = ""

            if "zip_file" in self.request.files and self.request.files["zip_file"][0]["content_type"] == 'application/zip':
                zip_file_name = self.request.files["zip_file"][0]["filename"]
                zip_file_contents = self.request.files["zip_file"][0]["body"]
                descriptor = zip_file_name.replace(".zip", "")

                zip_data = BytesIO()
                zip_data.write(zip_file_contents)
                zip_file = zipfile.ZipFile(zip_data)
                version = int(zip_file.read(f"{descriptor}/VERSION"))

                course_list = json.loads(zip_file.read(f"{descriptor}/courses.json"))[0]
                course_id = None
                course_basics = content.get_course_basics(course_id)
                content.specify_course_basics(course_basics, course_list[1], bool(course_list[3]))

                # Check whether course already exists.
                if content.has_duplicate_title(content.get_courses(), course_basics["id"], course_list[1]):
                    result = f"Error: A course with that title already exists."
                else:
                    course_details = content.get_course_details(course_id)
                    content.specify_course_details(course_details, course_list[2], convert_string_to_date(course_list[4]), convert_string_to_date(course_list[5]))
                    content.save_course(course_basics, course_details)

                    assignment_id_dict = {}
                    assignment_lists = json.loads(zip_file.read(f"{descriptor}/assignments.json"))
                    for assignment_list in assignment_lists:
                        assignment_id = None
                        assignment_basics = content.get_assignment_basics(course_basics["id"], assignment_id)
                        assignment_details = content.get_assignment_details(course_basics["id"], assignment_id)

                        content.specify_assignment_basics(assignment_basics, assignment_list[2], bool(assignment_list[4]))
                        #content.specify_assignment_details(assignment_details, assignment_list[3], convert_string_to_date(assignment_list[5]), convert_string_to_date(assignment_list[6]))

                        content.save_assignment(assignment_basics, assignment_details)
                        assignment_id_dict[assignment_list[1]] = assignment_basics["id"]

                    exercise_lists = json.loads(zip_file.read(f"{descriptor}/exercises.json"))
                    for exercise_list in exercise_lists:
                        exercise_id = None
                        exercise_basics = content.get_exercise_basics(course_basics["id"], assignment_id_dict[exercise_list[1]], exercise_id)
                        exercise_details = content.get_exercise_details(course_basics["id"], assignment_id_dict[exercise_list[1]], exercise_id)

                        content.specify_exercise_basics(exercise_basics, exercise_list[3], bool(exercise_list[4]))

                        answer_code = exercise_list[5]
                        answer_description = exercise_list[6]
                        hint = ""
                        max_submissions = int(exercise_list[7])
                        credit = exercise_list[8]
                        data_files = exercise_list[9]
                        back_end = exercise_list[10]
                        instructions = exercise_list[12]
                        output_type = exercise_list[13]
                        show_answer = bool(exercise_list[14])
                        show_student_submissions = bool(exercise_list[15])
                        show_expected = bool(exercise_list[16])
                        show_test_code = bool(exercise_list[17])
                        starter_code = exercise_list[18]
                        test_code = exercise_list[19]
                        date_created = convert_string_to_date(exercise_list[20])
                        date_updated = convert_string_to_date(exercise_list[21])

                        expected_text_output = ""
                        expected_image_output = ""
                        if expected_output == "txt":
                            expected_text_output = exercise_list[13]
                        else:
                            expected_image_output = exercise_list[13]

                        content.specify_exercise_details(exercise_details, instructions, back_end, output_type, answer_code, answer_description, hint, max_submissions, starter_code, test_code, credit, data_files, show_expected, show_test_code, show_answer, expected_output, date_created, date_updated)
                        content.save_exercise(exercise_basics, exercise_details)

                    result = "Success: The course was imported!"
            else:
                result = "Error: The uploaded file was not recognized as a zip file."

            self.render("profile_admin.html", page="admin", tab="import", admins=content.get_users_from_role(0, "administrator"), result=result, user_info=self.get_user_info(), is_administrator=self.is_administrator(), is_instructor=self.is_instructor(), is_assistant=self.is_assistant())
        except Exception as inst:
            render_error(self, traceback.format_exc())

