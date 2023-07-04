from BaseUserHandler import *

class IsTakingRestrictedAssignmentHandler(BaseUserHandler):
    async def get(self, user_id, assignment_id):
        try:
            self.write(json.dumps(self.content.is_taking_restricted_assignment(user_id, assignment_id), default=str))
        except Exception as inst:
            self.write(json.dumps(traceback.format_exc(), default=str))