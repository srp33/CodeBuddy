from BaseUserHandler import *

class SummarizeLogsHandler(BaseUserHandler):
    async def get(self):
        try:
            if self.is_administrator:
                pages = sorted(list(self.get_summary_dict().keys()))
                years, months, days = self.get_date_options()

                self.render("summarize_logs.html", pages=pages, years=years, months=months, days=days, user_info=self.user_info, is_administrator=self.is_administrator)
            else:
                self.render("permissions.html")
        except Exception as inst:
            render_error(self, traceback.format_exc())

    async def post(self):
        results = {"message": "", "table_rows": []}

        try:
            if self.is_administrator:
                query_details = json.loads(self.request.body)
                summary_dict = self.get_summary_dict()[query_details["page"]]

                hours_dict = {}

                for timestamp, data_dict in summary_dict.items():
                    timestamp_items = timestamp.split("-")
                    year = timestamp_items[0]
                    month = timestamp_items[1]
                    day = timestamp_items[2]
                    hour = int(timestamp_items[3])

                    if (query_details["year"] == "no_filter" or query_details["year"] == year) and (query_details["month"] == "no_filter" or query_details["month"] == month) and (query_details["day"] == "no_filter" or query_details["day"] == day):
                        if hour not in hours_dict:
                            hours_dict[hour] = [0, 0.0, {}]

                        hours_dict[hour][0] += data_dict['hits']
                        hours_dict[hour][1] += data_dict["duration"]

                        for user, hits in data_dict["user_hits"].items():
                            if user not in hours_dict[hour][2]:
                                hours_dict[hour][2][user] = 0

                            hours_dict[hour][2][user] += hits

                results["table_rows"] = []

                for hour, stats in sorted(hours_dict.items()):
                    avg_duration = stats[1] / stats[0]
                    avg_duration = f"{avg_duration:.3f}"

                    user_items = []
                    for user, num_hits in sorted(stats[2].items()):
                        user_items.append(f"{user} (hits: {num_hits})<br />")
                    user_text = "".join(user_items)

                    row = [f"{hour:2d}", stats[0], avg_duration, len(stats[2]), user_text]
                    results["table_rows"].append(row)
            else:
                results["message"] = "You do not have permission to access this page."
        except Exception as inst:
            results["message"] = traceback.format_exc()

        self.write(json.dumps(results, default=str))

    def get_summary_dict(self):
        log_dict = {}

        if os.path.exists("logs/summarized.json"):
            with open("logs/summarized.json") as json_file:
                log_dict = ujson.loads(json_file.read())
        
        return log_dict

    def get_date_options(self):
        years = []
        months = []
        days = []

        dateTimeObj = datetime.utcnow()
        currYear = str(dateTimeObj.year)
        yearAbrev = int(currYear)

        for i in range(2020, yearAbrev+1):
            years.append(str(i))

        for i in range(1, 13):
            months.append("{0:02d}".format(i))

        for i in range(1, 32):
            days.append("{0:02d}".format(i))

        return years, months, days