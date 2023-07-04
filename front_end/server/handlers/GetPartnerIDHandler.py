from BaseUserHandler import *

class GetPartnerIDHandler(BaseUserHandler):
    async def get(self, course_id, partner_name):
        partner_dict = await self.get_partner_info(course_id, True)

        # Determines whether the partner_key is a valid one while hiding student emails from the client side.
        if partner_name in partner_dict:
            self.write(json.dumps(partner_dict[partner_name], default=str))
        else:
            self.write(json.dumps({"error": "Invalid partner key"}, default=str))