from BaseUserHandler import *

class SubmitHandler(BaseUserHandler):
    async def post(self, course, assignment, exercise):
        out_dict = {"text_output": "", "image_output": "", "diff": "", "passed": False, "submission_id": ""}

        try:
            with open("/logs/progress.log", "a") as progress_file:
                progress_file.write("-------------------------------\nBegin debugging pair programming submission\n-------------------------------\n\n")

                user_id = self.get_user_id()

                progress_file.write(f"Successfully found user_id: {user_id}" + "\n")
                partners_dict = self.content.get_partner_info(course, user_id)

                progress_file.write(f"Successfully found partners_dict" + "\n")
                partner_id = partners_dict[self.get_body_argument("partner_key")] if self.get_body_argument("partner_key") else None

                progress_file.write(f"Successfully found partner_id: {partner_id}" + "\n")
                code = self.get_body_argument("user_code").replace("\r", "")
                exercise_basics = self.content.get_exercise_basics(course, assignment, exercise)
                exercise_details = self.content.get_exercise_details(course, assignment, exercise)
                assignment_details = self.content.get_assignment_details(course, assignment)
                progress_file.write(f"Successfully found exercise_basics, exercise_details, and assignment_details" + "\n")

                # Executes code and saves text, image, and test outputs in respective variables.
                text_output, image_output, tests = exec_code(self.settings_dict, code, exercise_basics, exercise_details, self.request)
                progress_file.write(f"Successfully executed code" + "\n")
                # The variables 'diff' and 'passed' refer to the solution code, while 'test_outcomes' contains diff and passed values for each test.
                diff, passed, test_outcomes = check_exercise_output(exercise_details, text_output, image_output, tests)
                progress_file.write(f"Successfully checked code against exercise_details" + "\n")
                progress_file.write(f"{'Submission passed' if passed else 'Submission failed'}" + "\n")

                out_dict["text_output"] = text_output.strip()
                out_dict["image_output"] = image_output
                out_dict["tests"] = test_outcomes
                out_dict["diff"] = format_output_as_html(diff)
                out_dict["passed"] = passed
                progress_file.write(f"Successfully set out_dict values" + "\n")
                out_dict["submission_id"] = self.content.save_submission(course, assignment, exercise, user_id, code, text_output, image_output, passed, tests, partner_id)

                progress_file.write(f"Successfully saved submission" + "\n")

                self.content.delete_presubmission(course, assignment, exercise, user_id)
                progress_file.write(f"Successfully deleted this exercise's presubmission for user: {user_id}" + "\n")

                exercise_score = self.content.get_exercise_score(course, assignment, exercise, user_id)
                progress_file.write(f"Successfully found old submission's score: {exercise_score}" + "\n")
                new_score = self.content.calc_exercise_score(assignment_details, passed)
                progress_file.write(f"Successfully calculated new submission's score: {new_score}" + "\n")

                if not exercise_score or exercise_score < new_score:
                    self.content.save_exercise_score(course, assignment, exercise, user_id, new_score)
                    progress_file.write(f"Successfully saved this exercise's score" + "\n")

                # Saves score for partner.
                if partner_id:
                    progress_file.write(f"Pair programming partner found" + "\n")
                    partner_exercise_score = self.content.get_exercise_score(course, assignment, exercise, partner_id)
                    progress_file.write(f"Successfully found partner's old submission score: {exercise_score}" + "\n")
                    partner_new_score = self.content.calc_exercise_score(assignment_details, passed)
                    progress_file.write(f"Successfully calculated partner's new submission score: {new_score}" + "\n")
                    if not partner_exercise_score or partner_exercise_score < partner_new_score:
                        self.content.save_exercise_score(course, assignment, exercise, partner_id, new_score)
                        progress_file.write(f"Successfully saved this exercise's score for {partner_id}" + "\n")


                progress_file.write("\nSuccessfully reached the end of save_submission!\n-------------------------------\n\n\n")

        except ConnectionError as inst:
            with open("/logs/progress.log", "a") as progress_file:
                progress_file.write("\nThe front-end server was unable to contact the back-end server.\n")
            out_dict["text_output"] = "The front-end server was unable to contact the back-end server."
            out_dict["passed"] = False
        except ReadTimeout as inst:
            with open("/logs/progress.log", "a") as progress_file:
                progress_file.write("\nYour solution timed out after {self.settings_dict['back_ends'][exercise_details['back_end']]['timeout_seconds']} seconds.\n")
            out_dict["text_output"] = f"Your solution timed out after {self.settings_dict['back_ends'][exercise_details['back_end']]['timeout_seconds']} seconds."
            out_dict["passed"] = False
        except Exception as inst:
            with open("/logs/progress.log", "a") as progress_file:
                progress_file.write("\nThe front-end server was unable to contact the back-end server.\n")
            out_dict["text_output"] = format_output_as_html(traceback.format_exc())
            out_dict["passed"] = False
        self.write(json.dumps(out_dict))
        
