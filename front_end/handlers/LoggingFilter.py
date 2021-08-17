import logging
import contextvars

class LoggingFilter(logging.Filter):
    def prepare(self):
        self.user_info_var = contextvars.ContextVar("user_info")

    def filter(self, record):
        try:
            user_info = self.user_info_var.get()

            if isinstance(user_info, str):
                user_id = user_info
            else:
                user_id = user_info["user_id"]
        except:
            user_id = "-"

        record.user_id = user_id

        return True

