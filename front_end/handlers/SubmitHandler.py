from BaseUserHandler import *

class SubmitHandler(BaseUserHandler):
    async def post(self, course, assignment, exercise):
        out_dict = {"text_output": "", "image_output": "", "diff": "", "passed": False, "submission_id": ""}

        try:
            user_id = self.get_user_id()
            partners_dict = self.content.get_partner_info(course, user_id)

            partner_id = partners_dict[self.get_body_argument("partner_key")] if self.get_body_argument("partner_key") else None
            code = self.get_body_argument("user_code").replace("\r", "")
            exercise_basics = self.content.get_exercise_basics(course, assignment, exercise)
            exercise_details = self.content.get_exercise_details(course, assignment, exercise)
            assignment_details = self.content.get_assignment_details(course, assignment)

            # Executes code and saves text, image, and test outputs in respective variables.
            text_output, image_output, tests = exec_code(self.settings_dict, code, exercise_basics, exercise_details, self.request)
            # The variables 'diff' and 'passed' refer to the solution code, while 'test_outcomes' contains diff and passed values for each test.
            diff, passed, test_outcomes = check_exercise_output(exercise_details, text_output, image_output, tests)

            out_dict["text_output"] = text_output.strip()
            out_dict["image_output"] = image_output
            out_dict["tests"] = test_outcomes
            out_dict["diff"] = format_output_as_html(diff)
            out_dict["passed"] = passed
            out_dict["submission_id"] = self.content.save_submission(course, assignment, exercise, user_id, code, text_output, image_output, passed, tests, partner_id)

            self.content.delete_presubmission(course, assignment, exercise, user_id)

            exercise_score = self.content.get_exercise_score(course, assignment, exercise, user_id)
            new_score = self.content.calc_exercise_score(assignment_details, passed)

            if not exercise_score or exercise_score < new_score:
                self.content.save_exercise_score(course, assignment, exercise, user_id, new_score)

            # Saves score for partner.
            if partner_id:
                partner_exercise_score = self.content.get_exercise_score(course, assignment, exercise, partner_id)
                partner_new_score = self.content.calc_exercise_score(assignment_details, passed)
                if not partner_exercise_score or partner_exercise_score < partner_new_score:
                    self.content.save_exercise_score(course, assignment, exercise, partner_id, new_score)

        except ConnectionError as inst:
            out_dict["text_output"] = "The front-end server was unable to contact the back-end server."
            out_dict["passed"] = False
        except ReadTimeout as inst:
            out_dict["text_output"] = f"Your solution timed out after {self.settings_dict['back_ends'][exercise_details['back_end']]['timeout_seconds']} seconds."
            out_dict["passed"] = False
        except Exception as inst:
            out_dict["text_output"] = format_output_as_html(traceback.format_exc())
            out_dict["passed"] = False
        self.write(json.dumps(out_dict))

