# <copyright_statement>
#   CodeBuddy - A learning management system for computer programming
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *

class PreferencesHandler(BaseUserHandler):
    async def get(self, user_id):
        try:
            ace_themes = ["ambiance", "chaos", "chrome", "clouds", "cobalt", "dracula", "github", "kr_theme", "monokai", "sqlserver", "terminal", "tomorrow", "xcode"]

            self.render("preferences.html", ace_themes=ace_themes, user_info=self.user_info, is_administrator=self.is_administrator)
        except Exception as inst:
            render_error(self, traceback.format_exc())

    async def post(self, user_id):
        if user_id != self.get_current_user():
            self.write(f"Error: The user identifiers do not match: {user_id} and {self.get_current_user()}.")
            return
        
        message = "Success! Preferences were saved."

        try:
            preferences_dict = ujson.loads(self.request.body)

            self.content.update_user_settings(user_id, preferences_dict)
        except Exception as inst:
            message = f"Error: The settings were not saved. {traceback.format_exc()}"

        self.write(message)