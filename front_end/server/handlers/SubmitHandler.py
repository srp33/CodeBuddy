from BaseUserHandler import *
from dateutil import parser

class SubmitHandler(BaseUserHandler):
    async def post(self, course_id, assignment_id, exercise_id):
        out_dict = {"message": "", "test_outputs": {}, "all_passed": False, "partner_name": None, "submission_id": ""}

        try:
            user_id = self.get_current_user()
            code = self.get_body_argument("code").replace("\r", "")
            date = parser.parse(self.get_body_argument("date"))
            partner_id = self.get_body_argument("partner_id", default=None)

            course_basics = self.get_course_basics(course_id)
            assignment_basics = self.content.get_assignment_basics(course_basics, assignment_id)

            assignment_details = self.get_assignment_details(course_basics, assignment_id)
            exercise_details = self.get_exercise_details(course_basics, assignment_basics, exercise_id)

            num_submissions = self.content.get_num_submissions(course_id, assignment_id, exercise_id, user_id)

            if exercise_details["max_submissions"] > 0 and num_submissions >= exercise_details["max_submissions"]:
                out_dict["message"] = "You have exceeded the maximum number of allowed submissions for this exercise."
                self.write(json.dumps(out_dict))
                return

            out_dict = exec_code(self.settings_dict, code, exercise_details["verification_code"], exercise_details, True)

            if out_dict["message"] == "":
                out_dict["all_passed"] = check_test_outputs(exercise_details, out_dict["test_outputs"])
                out_dict["submission_id"] = self.content.save_submission(course_id, assignment_id, exercise_id, user_id, code, out_dict["all_passed"], date, exercise_details, out_dict["test_outputs"], partner_id)

                if partner_id:
                    self.content.save_submission(course_id, assignment_id, exercise_id, partner_id, code, out_dict["all_passed"], date, exercise_details, out_dict["test_outputs"], user_id)

            #TODO: Combine these into fewer database calls.
            exercise_score = self.content.get_exercise_score(course_id, assignment_id, exercise_id, user_id)
            new_score = self.content.calc_exercise_score(assignment_details, out_dict["all_passed"])

            if not exercise_score or exercise_score < new_score:
                self.content.save_exercise_score(course_id, assignment_id, exercise_id, user_id, new_score)

            # Saves score for partner.
            if partner_id:
                partner_exercise_score = self.content.get_exercise_score(course_id, assignment_id, exercise_id, partner_id)
                partner_new_score = self.content.calc_exercise_score(assignment_details, out_dict["all_passed"])

                if not partner_exercise_score or partner_exercise_score < partner_new_score:
                    self.content.save_exercise_score(course_id, assignment_id, exercise_id, partner_id, new_score)

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

        self.write(json.dumps(out_dict))