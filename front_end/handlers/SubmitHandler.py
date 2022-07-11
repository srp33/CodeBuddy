from BaseUserHandler import *

class SubmitHandler(BaseUserHandler):
    async def post(self, course, assignment, exercise):
        out_dict = {"message": "", "test_outputs": {}, "all_passed": False, "submission_id": ""}

        try:
            user_id = self.get_user_id()
            partner_id = self.get_body_argument("partner_id") if self.get_body_argument("partner_id") else None

            code = self.get_body_argument("user_code").replace("\r", "")
            exercise_basics = self.content.get_exercise_basics(course, assignment, exercise)
            exercise_details = self.content.get_exercise_details(course, assignment, exercise)
            assignment_details = self.content.get_assignment_details(course, assignment)

            out_dict = exec_code(self.settings_dict, code, exercise_details["verification_code"], exercise_details, True)

            if out_dict["message"] == "":
                out_dict["all_passed"] = check_test_outputs(exercise_details, out_dict["test_outputs"])
                out_dict["submission_id"] = self.content.save_submission(course, assignment, exercise, user_id, code, out_dict["all_passed"], exercise_details, out_dict["test_outputs"], partner_id)

                if partner_id:
                    self.content.save_submission(course, assignment, exercise, partner_id, code, out_dict["all_passed"], exercise_details, out_dict["test_outputs"], user_id)

#TODO: Reenable this?
#            self.content.delete_presubmission(course, assignment, exercise, user_id)

            #TODO: Combine these into fewer database calls.
            exercise_score = self.content.get_exercise_score(course, assignment, exercise, user_id)
            new_score = self.content.calc_exercise_score(assignment_details, out_dict["all_passed"])

            if not exercise_score or exercise_score < new_score:
                self.content.save_exercise_score(course, assignment, exercise, user_id, new_score)

            # Saves score for partner.
            if partner_id:
                partner_exercise_score = self.content.get_exercise_score(course, assignment, exercise, partner_id)
                partner_new_score = self.content.calc_exercise_score(assignment_details, out_dict["all_passed"])
                if not partner_exercise_score or partner_exercise_score < partner_new_score:
                    self.content.save_exercise_score(course, assignment, exercise, partner_id, new_score)
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
