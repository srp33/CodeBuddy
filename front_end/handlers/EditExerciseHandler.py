from BaseUserHandler import *
import datetime as dt

class EditExerciseHandler(BaseUserHandler):
    def get(self, course, assignment, exercise):
        try:
            if self.is_administrator() or self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                exercises = self.content.get_exercises(course, assignment)
                exercise_details = self.content.get_exercise_details(course, assignment, exercise)
                exercise_details["expected_text_output"] = format_output_as_html(exercise_details["expected_text_output"])
                next_prev_exercises = self.content.get_next_prev_exercises(course, assignment, exercise, exercises)

                self.render("edit_exercise.html", courses=self.content.get_courses(), assignments=self.content.get_assignments(course), exercises=exercises, tests=self.content.get_tests(course, assignment, exercise), exercise_statuses=self.content.get_exercise_statuses(course, assignment, self.get_user_info()["user_id"]), course_basics=self.content.get_course_basics(course), assignment_basics=self.content.get_assignment_basics(course, assignment), exercise_basics=self.content.get_exercise_basics(course, assignment, exercise), exercise_details=exercise_details, json_files=escape_json_string(json.dumps(exercise_details["data_files"])), next_exercise=next_prev_exercises["next"], prev_exercise=next_prev_exercises["previous"], code_completion_path=self.settings_dict["back_ends"][exercise_details["back_end"]]["code_completion_path"], back_ends=sort_nicely(self.settings_dict["back_ends"].keys()), result=None, user_info=self.get_user_info(), old_text_output='', old_image_output='', old_tests=[])
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, course, assignment, exercise):
        try:
            if not self.is_administrator() and not self.is_instructor_for_course(course) or self.is_assistant_for_course(course):
                self.render("permissions.html")
                return

            exercise_basics = self.content.get_exercise_basics(course, assignment, exercise)
            exercise_details = self.content.get_exercise_details(course, assignment, exercise)

            # Saves previous outputs and tests in case 'maintain_output' is selected.
            old_text_output = exercise_details["expected_text_output"]
            old_image_output = exercise_details["expected_image_output"]
            old_tests = exercise_details["tests"]
            # Saves number of old tests. If there are fewer old than new tests, CodeBuddy will later raise a warning.
            num_old_tests = len(old_tests)

            exercise_basics["title"] = self.get_body_argument("title").strip() #required
            exercise_basics["visible"] = self.get_body_argument("is_visible") == "Yes"
            exercise_details["instructions"] = self.get_body_argument("instructions").strip().replace("\r", "") #required
            exercise_details["back_end"] = self.get_body_argument("back_end")
            exercise_details["output_type"] = self.get_body_argument("output_type")
            exercise_details["answer_code"] = self.get_body_argument("answer_code_text").strip().replace("\r", "") #required (usually)
            exercise_details["answer_description"] = self.get_body_argument("answer_description").strip().replace("\r", "")
            exercise_details["hint"] = self.get_body_argument("hint").strip().replace("\r", "")
            exercise_details["max_submissions"] = int(self.get_body_argument("max_submissions"))
            exercise_details["starter_code"] = self.get_body_argument("starter_code_text").strip().replace("\r", "")
            exercise_details["credit"] = self.get_body_argument("credit").strip().replace("\r", "")
            exercise_details["show_expected"] = self.get_body_argument("show_expected") == "Yes"
            exercise_details["show_answer"] = self.get_body_argument("show_answer") == "Yes"
            exercise_details["show_student_submissions"] = self.get_body_argument("show_student_submissions") == "Yes"
            exercise_details["enable_pair_programming"] = self.get_body_argument("enable_pair_programming") == "Yes"
            exercise_details["hold_output_constant"] = self.get_body_argument("hold_output_constant") == "Yes"

            # Saves check_code into a temporary variable to reload into exercise_details after code has finished executing.
            exercise_details["check_code"] = ""
            check_code = self.get_body_argument("check_code_text").strip().replace("\r", "")

            tests = self.get_body_argument("tests_json")
            tests = json.loads(tests) if tests and len(tests) != 0 else []
            exercise_details["tests"] = tests

            old_files = self.get_body_argument("file_container")
            new_files = self.request.files
            if old_files and old_files != "{}":
                old_files = json.loads(old_files)
                exercise_details["data_files"] = old_files
            else:
                exercise_details["data_files"] = {}


            result = "Success: The exercise was saved!"

            any_response_counts = exercise_details["back_end"] == "any_response"

            if exercise_basics["title"] == "" or exercise_details["instructions"] == "" or (not any_response_counts and exercise_details["answer_code"] == ""):
                result = "Error: One of the required fields is missing."
            else:
                if self.content.has_duplicate_title(self.content.get_exercises(course, assignment), exercise_basics["id"], exercise_basics["title"]):
                    result = "Error: An exercise with that title already exists in this assignment."
                else:
                    if len(exercise_basics["title"]) > 80:
                        result = "Error: The title cannot exceed 80 characters."

                    else:
                        #if not re.match('^[a-zA-Z0-9()\s\"\-]*$', exercise_basics["title"]):
                        #    result = "Error: The title can only contain alphanumeric characters, spaces, hyphens, and parentheses."
                        #else:
                            if new_files:
                                data_files = {}
                                total_size = 0

                                #create data_files dictionary
                                for fileInput, fileContents in new_files.items():
                                    for i in range(len(fileContents)):
                                        data_files[fileContents[i]["filename"]] = fileContents[i]["body"].decode("utf-8")
                                        total_size += len(fileContents[i]["body"])

                                exercise_details["data_files"].update(data_files)

                                # Make sure total file size is not larger than 10 MB across all files.
                                if total_size > 10 * 1024 * 1024:
                                    result = f"Error: Your total file size is too large ({total_size} bytes)."

                            if exercise_basics['exists'] and exercise_details["hold_output_constant"]:
                                # Sets exercise_details["tests"] temporarily in order to check exercise output
                                exercise_details["expected_text_output"], exercise_details["expected_image_output"], exercise_details["tests"] = exec_code(self.settings_dict, exercise_details["answer_code"], exercise_basics, exercise_details)
                                diff, passed, test_outcomes = check_exercise_output(exercise_details, old_text_output, old_image_output, old_tests)

                                if not passed or not all(list(map(lambda x: x["passed"], test_outcomes))):
                                    result = "Error: new output does not match pre-existing output."
                                else:
                                    # Returns exercise_details['tests'] to its new tests.
                                    exercise_details["tests"] = tests

                            if not result.startswith("Error:"):
                                old_tests = []
                                old_text_output = old_image_output = ''

                                self.content.specify_exercise_basics(exercise_basics, exercise_basics["title"], exercise_basics["visible"])

                                self.content.specify_exercise_details(exercise_details, exercise_details["instructions"], exercise_details["back_end"], exercise_details["output_type"], exercise_details["answer_code"], exercise_details["answer_description"], exercise_details["hint"], exercise_details["max_submissions"], exercise_details["starter_code"], exercise_details["test_code"], exercise_details["credit"], exercise_details["data_files"], exercise_details["show_expected"], exercise_details["show_test_code"], exercise_details["show_answer"], exercise_details["show_student_submissions"], "", "", None, dt.datetime.now(), exercise_details["enable_pair_programming"], exercise_details["check_code"], exercise_details["tests"])
                                text_output, image_output, tests = exec_code(self.settings_dict, exercise_details["answer_code"], exercise_basics, exercise_details)

                                # Calculates number of empty test outputs to aid instructor in debugging.
                                empty_tests = list(filter(lambda x: x["text_output"] == "" and x["image_output"] == "", tests))

                                # Loads test outcomes into dictionary with test code.
                                tests_dict = []
                                for i in range(len(tests)):
                                    tests_dict.append({**tests[i], **exercise_details["tests"][i]})

                                exercise_details["tests"] = tests_dict
                                exercise_details["expected_text_output"] = text_output.strip()
                                exercise_details["expected_image_output"] = image_output

                                if not any_response_counts and text_output == "" and image_output == "" and len(empty_tests) == len(tests):
                                    result = f"Error: No output was produced."
                                else:
                                    # If some but not all of tests have empty outputs, the exercise will still be saved but the instructor will be flagged with all tests that didn't produce any output.
                                    if len(empty_tests) > 0:
                                        result = f"Warning: {len(empty_tests)} of your tests produced no output."

                                    if exercise:
                                        # Get scores from content (which also contains data about the number of submissions in an exercise)
                                        scores = self.content.get_exercise_scores(course, assignment, exercise)
                                        num_submissions = sum(list(map(lambda x: int(x[1]["num_submissions"]), scores)))
                                    else:
                                        num_submissions = 0

                                    # If number of tests is greater than before last save and number of submissions on this exercise is greater than zero, raise warning.
                                    if num_old_tests < len(tests) and num_submissions > 0:
                                        result = f"Warning: You have increased the number of tests, and this exercise already has {num_submissions} submissions. This will render the output of those submissions unviewable for students. However, their submission scores will not change."

                                    exercise_details["check_code"] = check_code
                                    exercise = self.content.save_exercise(exercise_basics, exercise_details)

                                    exercise_basics = self.content.get_exercise_basics(course, assignment, exercise)
                                    exercise_details = self.content.get_exercise_details(course, assignment, exercise)

            exercises = self.content.get_exercises(course, assignment)
            next_prev_exercises = self.content.get_next_prev_exercises(course, assignment, exercise, exercises)

            self.render("edit_exercise.html", courses=self.content.get_courses(), assignments=self.content.get_assignments(course), exercises=exercises, tests=self.content.get_tests(course, assignment, exercise), exercise_statuses=self.content.get_exercise_statuses(course, assignment, self.get_user_info()["user_id"]), course_basics=self.content.get_course_basics(course), assignment_basics=self.content.get_assignment_basics(course, assignment), exercise_basics=exercise_basics, exercise_details=exercise_details, json_files=escape_json_string(json.dumps(exercise_details["data_files"])), next_exercise=next_prev_exercises["next"], prev_exercise=next_prev_exercises["previous"], code_completion_path=self.settings_dict["back_ends"][exercise_details["back_end"]]["code_completion_path"], back_ends=sort_nicely(self.settings_dict["back_ends"].keys()), result=result, user_info=self.get_user_info(), old_text_output=old_text_output, old_image_output=old_image_output, old_tests=old_tests)
        except ConnectionError as inst:
            render_error(self, "The front-end server was unable to contact the back-end server.")
        except ReadTimeout as inst:
            render_error(self, f"Your solution timed out after {self.settings_dict['back_ends'][exercise_details['back_end']]['timeout_seconds']} seconds.")
        except Exception as inst:
            render_error(self, traceback.format_exc())
