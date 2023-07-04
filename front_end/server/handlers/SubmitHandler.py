from BaseUserHandler import *
from dateutil import parser

class SubmitHandler(BaseUserHandler):
    async def post(self, course_id, assignment_id, exercise_id):
        out_dict = {"message": "", "test_outputs": {}, "all_passed": False, "score": 0, "partner_name": None, "submission_id": ""}

        try:
            user_id = self.get_current_user()
            code = self.get_body_argument("code").replace("\r", "")
            date = parser.parse(self.get_body_argument("date"))
            partner_id = self.get_body_argument("partner_id")
            partner_id = None if partner_id == "" else partner_id

            course_basics = await self.get_course_basics(course_id)
            assignment_basics = await self.get_assignment_basics(course_basics, assignment_id)

            assignment_details = await self.get_assignment_details(course_basics, assignment_id)
            exercise_details = await self.get_exercise_details(course_basics, assignment_basics, exercise_id)

            if exercise_details["max_submissions"] > 0:
                num_submissions = await self.content.get_num_submissions(course_id, assignment_id, exercise_id, user_id)
            
                if num_submissions >= exercise_details["max_submissions"]:
                    out_dict["message"] = "You have exceeded the maximum number of allowed submissions for this exercise."
                    self.write(json.dumps(out_dict, default=str))
                    return

            out_dict = await exec_code(self.settings_dict, code, exercise_details["verification_code"], exercise_details, True)

            if out_dict["message"] == "":
                out_dict["all_passed"] = check_test_outputs(exercise_details, out_dict["test_outputs"])

                out_dict["score"] = self.calc_exercise_score(assignment_details, out_dict["all_passed"])

                out_dict["submission_id"] = await self.content.save_submission(course_id, assignment_id, exercise_id, user_id, code, out_dict["all_passed"], date, exercise_details, out_dict["test_outputs"], out_dict["score"], partner_id)

                if partner_id:
                    await self.content.save_submission(course_id, assignment_id, exercise_id, partner_id, code, out_dict["all_passed"], date, exercise_details, out_dict["test_outputs"], out_dict["score"], user_id)

                    out_dict["partner_name"] = self.content.get_user_info(partner_id)["name"]

                sanitize_test_outputs(exercise_details, out_dict["test_outputs"])
        except ConnectionError as inst:
            out_dict["message"] = "The front-end server was unable to contact the back-end server."
            out_dict["all_passed"] = False
        except ReadTimeout as inst:
            out_dict["message"] = f"Your solution timed out after {self.settings_dict['back_ends'][exercise_details['back_end']]['timeout_seconds']} seconds."
            out_dict["all_passed"] = False
        except Exception as inst:
            out_dict["message"] = format_output_as_html(traceback.format_exc())
            out_dict["all_passed"] = False

        self.write(json.dumps(out_dict, default=str))

    def calc_exercise_score(self, assignment_details, passed):
        if passed:
            if assignment_details["due_date"] and assignment_details["due_date"] < datetime.utcnow():
                if assignment_details["allow_late"]:
                    return 100 * assignment_details["late_percent"]
            else:
                return 100
        else:
            return 0