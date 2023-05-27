from BaseUserHandler import *

class PreferencesHandler(BaseUserHandler):
    def get(self, user_id):
        try:
            ace_themes = ["ambiance", "chaos", "chrome", "clouds", "cobalt", "dracula", "github", "kr_theme", "monokai", "sqlserver", "terminal", "tomorrow", "xcode"]
            self.render("preferences.html", page="preferences", code_completion_path="ace/mode/r", ace_themes=ace_themes, user_info=self.user_info, is_administrator=self.is_administrator)
        except Exception as inst:
            render_error(self, traceback.format_exc())

    def post(self, user_id):
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