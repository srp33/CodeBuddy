# <copyright_statement>
#   CodeBuddy - A learning management system for computer programming
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from helper import *
from BaseRequestHandler import *
import traceback

class BaseOtherHandler(BaseRequestHandler):
    def get_current_user(self):
        user_id = super().get_current_user()

        if not user_id:
            return get_client_ip_address(self.request)

    def on_finish(self):
        try:
            log_page_access(self)
        except:
            print(f"Error occurred when attempting to log. {traceback.format_exc()}")
            pass

        super().on_finish()