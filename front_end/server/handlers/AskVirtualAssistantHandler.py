from BaseUserHandler import *

class AskVirtualAssistantHandler(BaseUserHandler):
    async def post(self, course_id, assignment_id, exercise_id):
        out_dict = {"message": "", "success": False}

        try:
            course_details = await self.get_course_details(course_id)

            virtual_assistant_max_per_exercise = course_details["virtual_assistant_config"]["max_per_exercise"]

            if virtual_assistant_max_per_exercise > 0:
                virtual_assistant_interactions = self.content.get_virtual_assistant_interactions(course_id, assignment_id, exercise_id, self.user_info["user_id"])

                if len(virtual_assistant_interactions) > virtual_assistant_max_per_exercise:
                    out_dict["message"] = f"You have reach the limit ({virtual_assistant_max_per_exercise}) for questions that can be asked on this exercise."

            if out_dict["message"] == "":
                question = self.get_body_argument("question").strip()

                # TODO: OpenAI API
                response = "This is the response."

                self.content.save_virtual_assistant_interaction(course_id, assignment_id, exercise_id, self.get_current_user(), question, response)

                out_dict["message"] = response
                out_dict["success"] = True
        # except ConnectionError as inst:
        #     out_dict["message"] = "The front-end server was unable to contact the back-end server."
        # except ReadTimeout as inst:
        #     out_dict["message"] = f"Your solution timed out after {self.settings_dict['back_ends'][exercise_details['back_end']]['timeout_seconds']} seconds."
        except Exception as inst:
            out_dict["message"] = traceback.format_exc()

        self.write(json.dumps(out_dict, default=str))