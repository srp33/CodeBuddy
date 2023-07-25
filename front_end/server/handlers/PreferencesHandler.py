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
            self.render("preferences.html", page="preferences", code_completion_path="ace/mode/r", ace_themes=ace_themes, user_info=self.user_info, is_administrator=self.is_administrator)
        except Exception as inst:
            render_error(self, traceback.format_exc())

    async def post(self, user_id):
        try:
            ace_theme = self.get_body_argument("ace_theme")
            use_auto_complete = self.get_body_argument("use_auto_complete") == "Yes"
            use_studio_mode = self.get_body_argument("use_studio_mode") == "Yes"
            enable_vim = self.get_body_argument("enable_vim") == "Yes"

            self.content.update_user_settings(user_id, ace_theme, use_auto_complete, use_studio_mode, enable_vim)
            
            ace_themes = ["ambiance", "chaos", "chrome", "clouds", "cobalt", "dracula", "github", "kr_theme", "monokai", "sqlserver", "terminal", "tomorrow", "xcode"]

            self.render("preferences.html", page="preferences", code_completion_path="ace/mode/r", ace_themes=ace_themes, user_info=self.user_info, is_administrator=self.is_administrator)
        except Exception as inst:
            render_error(self, traceback.format_exc())