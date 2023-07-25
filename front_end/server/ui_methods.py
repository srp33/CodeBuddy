# <copyright_statement>
#   CodeBuddy - A learning management system for computer programming
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

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
	if manifest is None or ('DEBUG' in os.environ and os.environ['DEBUG'] == 'true'):
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

# shamelessly stolen from https://pynative.com/python-serialize-datetime-into-json/
class DateTimeEncoder(json.JSONEncoder):
        #Override the default method
        def default(self, obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()

# custom json encoding function that can handle Datetime objects
def jsonify(handler, data):
	return json.dumps(data, cls=DateTimeEncoder)