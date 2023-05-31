from BaseUserHandler import *
import os
import urllib.request

class ExternalSiteHandler(BaseUserHandler):
    async def get(self, course_id, assignment_id, encoded_url):
        try:
            url = urllib.parse.unquote(encoded_url)

            assignment_details = self.get_assignment_details(self.get_course_basics(course_id), assignment_id)

            if url not in assignment_details["allowed_external_urls"]:
                return self.write("Access to {url} is not allowed for this course")

            url_hash = md5_hash_string(url)
            cache_file_path = f"/tmp/{url_hash}"

            if os.path.exists(cache_file_path):
                with open(cache_file_path, "rb") as cache_file:
                    content = cache_file.read()
            else:
                content = urllib.request.urlopen(url).read()

                with open(cache_file_path, "wb") as cache_file:
                    cache_file.write(content)

            if url.endswith(".html"):
                self.set_header('Content-type', "text/html; charset=UTF-8")
            elif url.endswith(".pdf"):
                self.set_header('Content-type', "application/pdf")
            else:
                return self.write(f"The specified URL {url} is invalid because it does not have a valid ending.")

            self.write(content)
        except Exception as inst:
            return self.write(f"An error occurred when attempting to access {url}. {traceback.format_exc()}")