from BaseUserHandler import *

class GetPartnerIDHandler(BaseUserHandler):
    def get(self, course, partner_name):
        partner_dict = self.content.get_partner_info(course, self.get_user_info()["user_id"])

        # Determines whether the partner_key is a valid one while hiding student emails from the client side.
        if partner_name in partner_dict:
            self.write(json.dumps(partner_dict[partner_name]))
        else:
            self.write(json.dumps({"error": "Invalid partner key"}))
