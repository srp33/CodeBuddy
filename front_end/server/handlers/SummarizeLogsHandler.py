from BaseUserHandler import *

class SummarizeLogsHandler(BaseUserHandler):
    async def get(self):
        try:
            if self.is_administrator:
                years, months, days = get_list_of_dates()
                self.render("summarize_logs.html", filter_list = sorted(self.content.get_root_dirs_to_log()), years=years, months=months, days=days, show_table=False, user_info=self.user_info, is_administrator=self.is_administrator)
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    async def post(self):
        try:
            if not self.is_administrator:
                self.render("permissions.html")
                return

            filter = self.get_body_argument("filter_select")
            year = self.get_body_argument("year_select")
            if year != "No filter":
                year = year[2:]
            month = self.get_body_argument("month_select")
            day = self.get_body_argument("day_select")
            log_file = self.get_body_argument("file_select")
            if log_file == "Select file":
                log_file = "logs/summarized/HitsAnyUser.tsv.gz"
            years, months, days = get_list_of_dates()

            self.render("summarize_logs.html", filter = filter, filter_list = sorted(self.content.get_root_dirs_to_log()), years=years, months=months, days=days, log_dict=self.content.get_log_table_contents(log_file, year, month, day), show_table=True, user_info=self.user_info, is_administrator=self.is_administrator)
        except Exception as inst:
            render_error(self, traceback.format_exc())