from BaseUserHandler import *
import hashlib
import os
import urllib.request

class ExternalSiteHandler(RequestHandler):
    async def get(self, url):
        try:
            # For some reason, the web server strips off the second forward slash
            url = re.sub(r"https://?", "https://", url)
            url = re.sub(r"http://?", "http://", url)

            settings_dict = load_yaml_dict(read_file("../Settings.yaml"))

            if url in settings_dict["allowed_external_urls"]:
                url_hash = hashlib.md5(url.encode()).hexdigest()
                cache_file_path = f"/tmp/cache/{url_hash}"

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

                self.write(content)
            else:
                render_error(self, "You are not allowed to access this resource via this site.")
        except Exception as inst:
            render_error(self, traceback.format_exc())
