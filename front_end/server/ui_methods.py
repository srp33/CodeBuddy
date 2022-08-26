import os
import json
import datetime
from helper import read_file

version = None
def get_version(handler):
	global version
	if version is None:
		version = read_file('../VERSION')
	return version

def has_entrypoint(handler):
	return hasattr(handler, 'entrypoint')

manifest = None

def _load_manifest():
	global manifest
	if manifest is None or 'DEBUG' in os.environ:
		manifest = json.loads(read_file('static/manifest.json'))
	return manifest

def get_assets(handler):
	entrypoint = getattr(handler, 'entrypoint', '')
	manifest = _load_manifest()
	js = []
	css = []
	if entrypoint in manifest and 'js' in manifest[entrypoint]:
		js = manifest[entrypoint]['js']
	if entrypoint in manifest and 'css' in manifest[entrypoint]:
		css = manifest[entrypoint]['css']
	if type(js) == str:
		js = [js]
	if type(css) == str:
		css = [css]
	return (js, css)

# shamelessly stoken from https://pynative.com/python-serialize-datetime-into-json/
class DateTimeEncoder(json.JSONEncoder):
        #Override the default method
        def default(self, obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()

# custom json encoding function that can handle Datetime objects
def jsonify(handler, data):
	return json.dumps(data, cls=DateTimeEncoder)
