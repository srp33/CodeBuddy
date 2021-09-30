from BaseUserHandler import *
import urllib.request

class ExternalSiteHandler(RequestHandler):
    async def get(self, url):
        try:
            settings_dict = load_yaml_dict(read_file("/Settings.yaml"))

            if url in settings_dict["allowed_external_urls"]:
                content = urllib.request.urlopen(url).read()

                if url.endswith(".html"):
                    self.set_header('Content-type', "text/html; charset=UTF-8")
                elif url.endswith(".pdf"):
                    self.set_header('Content-type', "application/pdf")

                self.write(content)
            else:
                render_error(self, "You are not allowed to access this resource via this site.")
        except Exception as inst:
            render_error(self, traceback.format_exc())
