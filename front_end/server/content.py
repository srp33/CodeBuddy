# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

import atexit
import random
import gzip
from helper import *
from imgcompare import *
import json
import math
import re
import sqlite3
import traceback
from yaml import load
#import zipfile

# IMPORTANT: When creating/modifying queries that include any user input,
#            please follow the recommendations on this page:
#            https://realpython.com/prevent-python-sql-injection/

BLANK_IMAGE = "/9j/4AAQSkZJRgABAQEAlgCWAAD/2wBDAAIBAQEBAQIBAQECAgICAgQDAgICAgUEBAMEBgUGBgYFBgYGBwkIBgcJBwYGCAsICQoKCgoKBggLDAsKDAkKCgr/2wBDAQICAgICAgUDAwUKBwYHCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgr/wAARCALQA8ADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD9/KKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA//Z"

class Content:
    def __init__(self, settings_dict):
        self.settings_dict = settings_dict
        db_file_path = "database/CodeBuddy.db"

        self.conn = open_db(db_file_path)
        self.conn.row_factory = sqlite3.Row

        # Add user-defined function(s)
        self.conn.create_function("adjust_assignment_score", 2, adjust_assignment_score)

        # See https://phiresky.github.io/blog/2020/sqlite-performance-tuning/
        self.execute("PRAGMA foreign_keys=OFF")
        self.execute("PRAGMA cache_size=1000000")
        self.execute("PRAGMA mmap_size=100000000")
        self.execute("PRAGMA temp_store=MEMORY")

        journal_mode = self.settings_dict['db_journal_mode']
        self.execute(f"PRAGMA journal_mode={journal_mode}")

        if journal_mode == "WAL":
            self.execute("PRAGMA wal_autocheckpoint = 1000")
            self.execute("PRAGMA busy_timeout = 5000")

        self.scores_statuses_temp_tables_sql = read_file("query_templates/scores_statuses.sql")

        atexit.register(self.close)

    # def is_connection_open(self):
    #     try:
    #         # Attempt to access the total_changes attribute
    #         self.conn.total_changes
    #         return True
    #     except sqlite3.ProgrammingError:
    #         return False

    def final_commit(self):
        if self.settings_dict['db_journal_mode'] == "WAL":
            self.conn.execute('PRAGMA wal_checkpoint(FULL)')

    def close(self):
        #  if self.is_connection_open():
        #     if self.settings_dict['db_journal_mode'] == "WAL":
        #         self.conn.execute('PRAGMA wal_checkpoint(FULL)')

        try:
            self.conn.close()
        except:
            print("An error occurred when attempting to close the database connection.")
            print(traceback.format_exc())

    def execute(self, sql, params=()):
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        lastrowid = cursor.lastrowid
        cursor.close()

        return lastrowid
    
    # def execute_and_get_num_updated_rows(self, sql, params=()):
    #     cursor = self.conn.cursor()
    #     cursor.execute(sql, params)
    #     self.conn.commit()

    #     rows_updated = cursor.rowcount

    #     cursor.close()

    #     return rows_updated
    
    def execute_multiple(self, sql_statements, params_list, lastrowid_index=-1):
        if len(sql_statements) != len(params_list):
            raise Exception(f"The size of sql_statements ({len(sql_statements)}) must be identical to the size of param_tuples ({len(params_list)}).")

        lastrowid = -1
        exception = None
        cursor = self.conn.cursor()

        try:
            cursor.execute("BEGIN TRANSACTION")

            for i, sql in enumerate(sql_statements):
                cursor.execute(sql, params_list[i])

                if i == lastrowid_index:
                    lastrowid = cursor.lastrowid

            self.conn.commit()
        except sqlite3.Error as e:
            exception = e
            self.conn.rollback()
        finally:
            cursor.close()

        if exception is not None:
            raise exception

        return lastrowid

    def fetchone(self, sql, params=()):
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        result = cursor.fetchone()
        cursor.close()

        return result

    def fetchall(self, sql, params=()):
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        result = cursor.fetchall()
        cursor.close()

        return result

    # This function creates tables as they were in version 5. Subsequent changes
    #   to the database are implemented as migration scripts.
    def create_database_tables(self):
        print("Creating the initial database schema...")
        self.execute('''CREATE TABLE IF NOT EXISTS metadata (version integer NOT NULL);''')
        self.execute('''INSERT INTO metadata (version) VALUES (5);''')

        self.execute('''CREATE TABLE IF NOT EXISTS users (
                          user_id text PRIMARY KEY,
                          name text,
                          given_name text,
                          family_name text,
                          picture text,
                          locale text,
                          ace_theme text NOT NULL DEFAULT "tomorrow");''')

        self.execute('''CREATE TABLE IF NOT EXISTS permissions (
                          user_id text NOT NULL,
                          role text NOT NULL,
                          course_id integer,
                        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE CASCADE
                     );''')

        self.execute('''CREATE TABLE IF NOT EXISTS course_registration (
                          user_id text NOT NULL,
                          course_id integer NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE ON UPDATE CASCADE
                     );''')

        self.execute('''CREATE TABLE IF NOT EXISTS courses (
                          course_id integer PRIMARY KEY AUTOINCREMENT,
                          title text NOT NULL UNIQUE,
                          introduction text,
                          visible integer NOT NULL,
                          passcode text,
                          date_created timestamp NOT NULL,
                          date_updated timestamp NOT NULL
                     );''')

        self.execute('''CREATE TABLE IF NOT EXISTS assignments (
                          course_id integer NOT NULL,
                          assignment_id integer PRIMARY KEY AUTOINCREMENT,
                          title text NOT NULL,
                          introduction text,
                          visible integer NOT NULL,
                          start_date timestamp,
                          due_date timestamp,
                          allow_late integer,
                          late_percent real,
                          view_answer_late integer,
                          has_timer int NOT NULL,
                          hour_timer int,
                          minute_timer int,
                          date_created timestamp NOT NULL,
                          date_updated timestamp NOT NULL,
                        FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE ON UPDATE CASCADE
                     );''')

        self.execute('''CREATE TABLE IF NOT EXISTS problems (
                          course_id integer NOT NULL,
                          assignment_id integer NOT NULL,
                          problem_id integer PRIMARY KEY AUTOINCREMENT,
                          title text NOT NULL,
                          visible integer NOT NULL,
                          answer_code text NOT NULL,
                          answer_description text,
                          hint text,
                          max_submissions integer NOT NULL,
                          credit text,
                          data_url text,
                          data_file_name text,
                          data_contents text,
                          back_end text NOT NULL,
                          expected_text_output text NOT NULL,
                          expected_image_output text NOT NULL,
                          instructions text NOT NULL,
                          output_type text NOT NULL,
                          show_answer integer NOT NULL,
                          show_student_submissions integer NOT NULL,
                          show_expected integer NOT NULL,
                          show_test_code integer NOT NULL,
                          test_code text,
                          date_created timestamp NOT NULL,
                          date_updated timestamp NOT NULL,
                          FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE ON UPDATE CASCADE,
                          FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE CASCADE ON UPDATE CASCADE
                     );''')

        self.execute('''CREATE TABLE IF NOT EXISTS submissions (
                          course_id integer NOT NULL,
                          assignment_id integer NOT NULL,
                          problem_id integer NOT NULL,
                          user_id text NOT NULL,
                          submission_id integer NOT NULL,
                          code text NOT NULL,
                          text_output text NOT NULL,
                          image_output text NOT NULL,
                          passed integer NOT NULL,
                          date timestamp NOT NULL,
                        FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (problem_id) REFERENCES problems (problem_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        PRIMARY KEY (course_id, assignment_id, problem_id, user_id, submission_id)
                     );''')

        self.execute('''CREATE TABLE IF NOT EXISTS scores (
                          course_id integer NOT NULL,
                          assignment_id integer NOT NULL,
                          problem_id integer NOT NULL,
                          user_id text NOT NULL,
                          score real NOT NULL,
                        FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (problem_id) REFERENCES problems (problem_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        PRIMARY KEY (course_id, assignment_id, problem_id, user_id)
                     );''')

        self.execute('''CREATE TABLE IF NOT EXISTS user_assignment_start (
                          user_id text NOT NULL,
                          course_id text NOT NULL,
                          assignment_id text NOT NULL,
                          start_time timestamp NOT NULL,
                        FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE CASCADE
                     );''')

    def get_database_version(self):
        sql = "SELECT COUNT(*) AS count FROM sqlite_master"

        # This tells us whether we have created the initial database schema.
        # If not, create it.
        num_tables = self.fetchone(sql)["count"]

        if num_tables == 0:
            self.create_database_tables()
            return 5

        sql = '''SELECT MAX(version) AS version
                 FROM metadata'''

        return self.fetchone(sql)["version"]

    def update_database_version(self, version):
        print(f"Updating database to version {version}")

        sql = '''DELETE FROM metadata'''
        self.execute(sql)

        sql = '''INSERT INTO metadata (version)
                 VALUES (?)'''
        self.execute(sql, (version,))

        print(f"Done updating database to version {version}")

    def find_when_content_updated(self):
        sql = '''SELECT scope, when_updated
                 FROM when_content_updated'''

        updated_dict = {}

        try:
            for row in self.fetchall(sql):
                updated_dict[row["scope"]] = str(row["when_updated"])
        except:
            print(traceback.format_exc())

        return updated_dict
    
    def update_when_content_updated(self, scope):
        sql = '''UPDATE when_content_updated
                 SET when_updated = datetime('now')
                 WHERE scope = ?'''

        try:
            self.execute(sql, (scope, ))
        except:
            print(traceback.format_exc())

    def update_all_when_content_updated(self):
        sql = '''UPDATE when_content_updated
                 SET when_updated = datetime('now')'''

        self.execute(sql, ())

    def delete_content_updated(self, scope):
        sql = '''DELETE FROM when_content_updated
                 WHERE scope = ?'''

        try:
            self.execute(sql, (scope, ))
        except:
            print(traceback.format_exc())

    def set_user_assignment_start_time(self, course_id, assignment_id, assignment_details, user_id, user_start_time):
        sql = '''INSERT INTO user_assignment_starts (course_id, assignment_id, user_id, start_time)
                 VALUES (?, ?, ?, ?)'''

        self.execute(sql, (course_id, assignment_id, user_id, user_start_time,))

        return get_student_timer_status(self, course_id, assignment_id, assignment_details, user_id, user_start_time=user_start_time)

    def end_timed_assignment_early(self, course_id, assignment_id, user_id):
        sql = '''UPDATE user_assignment_starts
                 SET ended_early = 1
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND user_id = ?'''

        self.execute(sql, (course_id, assignment_id, user_id,))

    def get_user_assignment_timer_status(self, course_id, assignment_id, user_id):
        sql = '''SELECT start_time, ended_early
                 FROM user_assignment_starts
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND user_id = ?'''

        row = self.fetchone(sql, (course_id, assignment_id, user_id,))
        if row:
            return localize_datetime(row["start_time"]), row["ended_early"]

        return None, None

    def is_taking_timed_assignment(self, user_id, assignment_id):
        sql = '''SELECT ((julianday(datetime('now')) - julianday(latest_start_time)) * 24 * 60) < minute_limit AS is_timed,
                   ended_early,
                   is_restricted
                 FROM
                 (
                    SELECT (IFNULL(ate.hour_timer, a.hour_timer) * 60 + IFNULL(ate.minute_timer, a.minute_timer)) AS minute_limit,
                    MAX(start_time) AS latest_start_time, 
                    uas.ended_early,
                    a.restrict_other_assignments = 1 AS is_restricted
                  FROM user_assignment_starts uas
			            INNER JOIN assignments a
			               ON uas.course_id = a.course_id
				            AND uas.assignment_id = a.assignment_id
                  LEFT JOIN assignment_timer_exceptions ate
			               ON ate.course_id = a.course_id
                     AND ate.user_id = ?
                  WHERE uas.user_id = ?
                    AND a.assignment_id != ?
			              AND a.has_timer = 1
		              )'''

        row = self.fetchone(sql, (user_id, user_id, assignment_id, ))
        if row:
            is_timed = row["is_timed"] and not row["ended_early"]
            is_restricted = is_timed and row["is_restricted"]

            return is_timed, is_restricted

        return False, False

    def get_timer_statuses(self, course_id, assignment_id, assignment_details):
        user_dict = {}

        sql = '''SELECT user_id, start_time, ended_early
                 FROM user_assignment_starts
                 WHERE course_id = ?
                   AND assignment_id = ?'''

        for row in self.fetchall(sql, (course_id, assignment_id,)):
            # user_start_time = datetime.strftime(row["start_time"], "%a, %d %b %Y %H:%M:%S %Z")
            user_start_time = localize_datetime(row["start_time"])

            timer_status, __, __, __, __ = get_student_timer_status(self, course_id, assignment_id, assignment_details, row["user_id"], user_start_time, bool(row["ended_early"]))

            user_dict[row["user_id"]] = timer_status

        return user_dict

    # def has_user_assignment_start_timer_ended(self, course_id, assignment_id, start_time):
    #     if not start_time:
    #         return False

    #     curr_time = get_current_datetime()
    #     start_time = datetime.strptime(start_time, "%a, %d %b %Y %H:%M:%S ")

    #     sql = '''SELECT hour_timer, minute_timer
    #              FROM assignments
    #              WHERE course_id = ?
    #                AND assignment_id = ?'''

    #     row = self.fetchone(sql, (course_id, assignment_id,))

    #     if row:
    #         elapsed_time = curr_time - start_time
    #         seconds = elapsed_time.total_seconds()
    #         e_hours = math.floor(seconds/3600)
    #         e_minutes = math.floor((seconds/60) - (e_hours*60))
    #         e_seconds = (seconds - (e_minutes*60) - (e_hours*3600))

    #         if e_hours > int(row["hour_timer"]):
    #             return True
    #         elif e_hours == int(row["hour_timer"]) and e_minutes > int(row["minute_timer"]):
    #             return True
    #         elif e_hours == int(row["hour_timer"]) and e_minutes == int(row["minute_timer"]) and e_seconds > 0:
    #             return True

    #     return False

    def reset_user_assignment_start_timer(self, course_id, assignment_id, user_id):
        sql = '''DELETE FROM user_assignment_starts
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND user_id = ?'''

        self.execute(sql, (course_id, assignment_id, user_id))

    def user_exists(self, user_id):
        sql = '''SELECT user_id
                 FROM users
                 WHERE user_id = ?'''

        return self.fetchone(sql, (user_id,)) != None

    def administrator_exists(self):
        sql = '''SELECT COUNT(*) AS num_administrators
                 FROM permissions
                 WHERE role = "administrator"'''

        return self.fetchone(sql)["num_administrators"]

    def is_administrator(self, user_id):
        return self.user_has_role(user_id, 0, "administrator")

    def user_has_role(self, user_id, course_id, role):
        sql = '''SELECT COUNT(*) AS has_role
                 FROM permissions
                 WHERE role = ?
                   AND user_id = ?
                   AND course_id = ?'''

        return self.fetchone(sql, (role, user_id, course_id, ))["has_role"] > 0

    def get_users_from_role(self, course_id, role):
        sql = '''SELECT user_id
                 FROM permissions
                 WHERE role = ?
                   AND (course_id = ? OR course_id IS NULL)'''

        rows = self.fetchall(sql, (role, course_id,))
        return [row["user_id"] for row in rows]        

    def get_users_to_manage(self, pattern):
        sql = '''SELECT DISTINCT u.user_id, u.name, u.research_cohort
                 FROM users u
                 LEFT JOIN permissions p
                   ON u.user_id = p.user_id
                 WHERE (p.role IS NULL OR p.role != 'administrator')
                   AND (u.user_id LIKE ? OR u.name LIKE ?)
                 ORDER BY u.name'''

        rows = self.fetchall(sql, (pattern, pattern,))
        return [{"user_id": row["user_id"], "name": row["name"], "research_cohort": row["research_cohort"]} for row in rows]

    def set_user_dict_defaults(self, user_dict):
        if "name" not in user_dict:
            user_dict["name"] = "[Unknown name]"
        if "given_name" not in user_dict:
            user_dict["given_name"] = "[Unknown given name]"
        if "family_name" not in user_dict:
            user_dict["family_name"] = "[Unknown family name]"
        if "locale" not in user_dict:
            user_dict["locale"] = ""

    def add_user(self, user_id, user_dict):
        self.set_user_dict_defaults(user_dict)

        sql = '''INSERT INTO users (user_id, name, given_name, family_name, locale, ace_theme, email_address, research_cohort)
                 VALUES (?, ?, ?, ?, ?, ?, ?, (SELECT CASE WHEN RANDOM() >= 0.5 THEN "A" ELSE "B" END))'''

        self.execute(sql, (user_id, user_dict["name"], user_dict["given_name"], user_dict["family_name"], user_dict["locale"], "tomorrow", user_dict["email_address"]))

        self.update_when_content_updated("user")

    def register_user_for_course(self, course_id, user_id):
        sql = '''INSERT INTO course_registrations (course_id, user_id)
                 VALUES (?, ?)'''

        self.execute(sql, (course_id, user_id,))

        self.update_when_content_updated("user")
        self.update_when_content_updated(str(course_id))

    def unregister_user_from_course(self, course_id, user_id):
        self.execute('''DELETE FROM course_registrations
                        WHERE course_id = ?
                          AND user_id = ?''', (course_id, user_id, ))

        self.execute('''DELETE FROM scores
                        WHERE course_id = ?
                          AND user_id = ?''', (course_id, user_id, ))

        self.execute('''DELETE FROM submissions
                        WHERE course_id = ?
                          AND user_id = ?''', (course_id, user_id, ))

        self.execute('''DELETE FROM user_assignment_starts
                        WHERE course_id = ?
                          AND user_id = ?''', (course_id, user_id, ))

        self.execute('''DELETE FROM assignment_early_exceptions
                        WHERE course_id = ?
                          AND user_id = ?''', (course_id, user_id, ))

        self.execute('''DELETE FROM assignment_late_exceptions
                        WHERE course_id = ?
                          AND user_id = ?''', (course_id, user_id, ))

        self.execute('''DELETE FROM assignment_timer_exceptions
                        WHERE course_id = ?
                          AND user_id = ?''', (course_id, user_id, ))
        
        self.update_when_content_updated("user")
        self.update_when_content_updated(str(course_id))

    def is_user_registered(self, course_id, user_id):
        sql = '''SELECT 1
                 FROM course_registrations
                 WHERE course_id = ?
                   AND user_id = ?'''

        if self.fetchone(sql, (course_id, user_id,)):
            return True

        return False

    def get_user_info(self, user_id):
        null_user_info = {"user_id": None, "name": None, "given_name": None, "family_name": None, "locale": None, "email_address": None, "ace_theme": None, "use_auto_complete": True, "use_studio_mode": False, "enable_vim": False, "research_cohort": "None"}

        sql = '''SELECT *
                 FROM users
                 WHERE user_id = ?'''

        user = self.fetchone(sql, (user_id,))

        if not user:
            return null_user_info

        return {"user_id": user_id, "name": user["name"], "given_name": user["given_name"], "family_name": user["family_name"], "locale": user["locale"], "email_address": user["email_address"], "ace_theme": user["ace_theme"], "use_auto_complete": user["use_auto_complete"], "use_studio_mode": user["use_studio_mode"], "enable_vim": user["enable_vim"], "research_cohort": user["research_cohort"]}

    def add_permissions(self, course_id, user_id, role):
        sql = '''SELECT role
                 FROM permissions
                 WHERE user_id = ?
                   AND (course_id = ? OR course_id IS NULL)'''

        # Admins are not assigned to a particular course.
        if not course_id:
            course_id = 0

        role_exists = self.fetchone(sql, (user_id, int(course_id),)) != None

        if role_exists:
            sql = '''UPDATE permissions
                     SET role = ?, course_id = ?
                     WHERE user_id = ?'''

            self.execute(sql, (role, course_id, user_id,))
        else:
            sql = '''INSERT INTO permissions (user_id, role, course_id)
                     VALUES (?, ?, ?)'''

            self.execute(sql, (user_id, role, course_id,))

        if course_id != 0:
            self.update_when_content_updated(str(course_id))

        self.update_when_content_updated("user")            

    def remove_course_permissions(self, course_id, user_id, role):
        sql = '''DELETE FROM permissions
                 WHERE user_id = ?
                   AND role = ?
                   AND (course_id = ? OR course_id IS NULL)'''

        # Admins are not assigned to a particular course.
        if not course_id:
            course_id = "0"

        self.execute(sql, (user_id, role, int(course_id),))

        if course_id != "0":
            self.update_when_content_updated(course_id)

        self.update_when_content_updated("user")

    def add_admin_permissions(self, user_id):
        self.add_permissions(None, user_id, "administrator")
        self.update_when_content_updated("user")

    def get_user_count(self):
        sql = '''SELECT COUNT(*) AS count
                 FROM users'''

        return self.fetchone(sql)["count"]

    def get_all_courses(self):
        courses = []

        sql = '''SELECT course_id, title, visible, introduction, passcode, highlighted
                 FROM courses
                 WHERE visible = 1
                 ORDER BY highlighted DESC, title'''

        for course in self.fetchall(sql):
            if course["visible"] or show_hidden:
                course_basics = {"id": course["course_id"], "title": course["title"], "visible": course["visible"], "introduction": convert_markdown_to_html(course["introduction"]), "passcode": course["passcode"], "highlighted": course["highlighted"], "exists": True}
                courses.append([course["course_id"], course_basics])

        return courses

    def get_registered_courses(self, user_id):
        registered_courses = []

        sql = '''SELECT r.course_id, c.title, c.introduction, 'student' AS role
                 FROM course_registrations r
                 INNER JOIN courses c
                   ON r.course_id = c.course_id
                 WHERE r.user_id = ?
                   AND c.visible = 1

                 UNION

                 SELECT c.course_id, c.title, c.introduction, p.role AS role
                 FROM permissions p
                 INNER JOIN courses c
                   ON p.course_id = 0 OR p.course_id = c.course_id
                 WHERE p.user_id = ?
                 ORDER BY c.title'''

        unique_course_ids = set()
        
        for course in self.fetchall(sql, (user_id, user_id, )):
            course_id = course["course_id"]

            if course_id not in unique_course_ids:
                unique_course_ids.add(course_id)

                course_basics = {"id": course_id, "title": course["title"], "introduction": convert_markdown_to_html(course["introduction"]), "role": course["role"]}

                registered_courses.append([course["course_id"], course_basics])

        return registered_courses

    # TODO: This function could probably be removed. get_exercise_statuses could be used in its place.
    def get_exercises(self, course_basics, assignment_basics, show_hidden=True):
        sql = '''SELECT exercise_id, title, visible, enable_pair_programming
                 FROM exercises
                 WHERE course_id = ?
                   AND assignment_id = ?
                 ORDER BY title'''

        exercises = []
        for exercise in self.fetchall(sql, (course_basics["id"], assignment_basics["id"],)):
            if exercise["visible"] or show_hidden:
                exercises.append(dict(exercise))

        exercises = sort_list_of_dicts_nicely(exercises, ["title", "exercise_id"])

        exercises2 = []
        for exercise in exercises:
            exercise_basics = {"enable_pair_programming": exercise["enable_pair_programming"], "id": exercise["exercise_id"], "title": exercise["title"], "visible": exercise["visible"], "exists": True, "assignment": assignment_basics}

            exercises2.append([exercise["exercise_id"], exercise_basics, course_basics['id'], assignment_basics['id']])

        return exercises2

    def get_partner_info(self, course_id, current_user_id):
        # Gets list of users.
        users = [x[1] for x in self.get_registered_students(course_id) if x[1]["id"] != current_user_id]

        # Adds users to dict to find duplicate names.
        user_duplicates_dict = {}
        for user in users:
            if user["name"] in user_duplicates_dict.keys():
                user_duplicates_dict[user["name"]].append({'id': user["id"], 'email': user['email']})
            else:
                user_duplicates_dict[user["name"]] = [{'id': user["id"], 'email': user['email']}]

        # Adds all users to a dictionary with name (and obscured email if applicable) as key and id as value.
        user_dict = {}
        for user in user_duplicates_dict:
            if len(user_duplicates_dict[user]) > 1:
                for user_info in user_duplicates_dict[user]:
                    user_dict[user + " — " + self.obscure_email(user_info['email'], list(map(lambda x: x['email'], user_duplicates_dict[user])))] = user_info['id']
            else:
                user_dict[user] = user_duplicates_dict[user][0]['id']

        return user_dict

    def obscure_email(self, full_email, all_emails):
        email = full_email.split("@")[0] if "@" in full_email else full_email
        email_end = full_email.split("@")[1] if "@" in full_email else full_email

        temp_email = email[0]
        for other_email in all_emails:
            other_email = other_email.split("@")[0] if "@" in other_email else other_email
            if other_email == email:
                pass
            else:
                for i in range(len(temp_email), len(min(email, other_email))):
                    if  temp_email == other_email[:i]:
                        temp_email = temp_email + email[i]
                    else:
                        break

        # Obscures all but essential characters of email.
        return temp_email + (("*")*(len(email)-len(temp_email))) + "@" + email_end

    def get_registered_students(self, course_id):
        registered_students = []

        sql = '''SELECT r.user_id, u.name, u.email_address
                 FROM course_registrations r
                 INNER JOIN users u
                   ON r.user_id = u.user_id
                 WHERE r.course_id = ?
                   AND r.user_id NOT IN (SELECT user_id FROM permissions
                                         WHERE course_id = ?)
                                         ORDER BY u.name'''

        for student in self.fetchall(sql, (course_id, course_id, )):
            student_info = {"id": student["user_id"], "name": student["name"], 'email': student['email_address']}
            registered_students.append([student["user_id"], student_info])

        return registered_students

    # Indicates whether or not a student has passed each assignment in the course.
    def get_assignment_statuses(self, course_id, user_id, show_hidden):
        course_basics = self.get_course_basics(course_id)

        sql = self.scores_statuses_temp_tables_sql + '''
SELECT
  sts.user_id,
  sts.assignment_id,
  a.title,
  a.visible,
  a.restrict_other_assignments,
  sts.num_exercises,
  sts.start_date,
  sts.due_date,
  sts.has_timer,
  sts.num_completed,
  sts.completed,
  sts.in_progress,
  sts.timer_has_ended,
  sts.num_times_pair_programmed,
  scr.score,
  IFNULL(a.custom_scoring, '') AS custom_scoring,
  IFNULL(ag.assignment_group_id, '') AS assignment_group_id,
  IFNULL(ag.title, '') AS assignment_group_title
FROM assignment_statuses sts
INNER JOIN assignment_scores scr
  ON sts.assignment_id = scr.assignment_id
  AND sts.user_id = scr.user_id
INNER JOIN valid_assignments a
  ON sts.assignment_id = a.assignment_id
LEFT JOIN valid_assignment_groups ag
  ON a.assignment_group_id = ag.assignment_group_id
'''

        statuses = []

        for row in self.fetchall(sql, (course_id, None, None, user_id)):
            assignment = dict(row)

            if assignment["visible"] or show_hidden:
                statuses.append(assignment)

        statuses2 = []

        # We have to check for this because otherwise the instructor has to make a submission before students will see the assignments.
        if len(statuses) == 0:
            for assignment_basics in self.get_assignments(course_basics, show_hidden):
                assignment_basics[2]["num_completed"] = 0
                assignment_basics[2]["num_exercises"] = 0
                assignment_basics[2]["completed"] = 0
                assignment_basics[2]["in_progress"] = 0
                assignment_basics[2]["score"] = 0
                assignment_basics[2]["custom_scoring"] = ""
                assignment_basics[2]["timer_has_ended"] = False

                statuses2.append([assignment_basics[0], assignment_basics[1],  assignment_basics[2]])
        else:
            for status in sort_list_of_dicts_nicely(statuses, ["assignment_group_title", "title", "assignment_id"]):
                assignment_dict = {"id": status["assignment_id"], "title": status["title"], "visible": status["visible"], "start_date": localize_datetime(status["start_date"]), "due_date": localize_datetime(status["due_date"]), "completed": status["completed"], "in_progress": status["in_progress"], "score": status["score"], "custom_scoring": status["custom_scoring"], "num_completed": status["num_completed"], "num_exercises": status["num_exercises"], "has_timer": status["has_timer"], "timer_has_ended": status["timer_has_ended"], "restrict_other_assignments": status["restrict_other_assignments"], "assignment_group_id": status["assignment_group_id"], "assignment_group_title": status["assignment_group_title"]}

                # if assignment_dict["start_date"]:
                #     assignment_dict["start_date"] = assignment_dict["start_date"].strftime('%Y-%m-%dT%H:%M:%SZ')
                # if assignment_dict["due_date"]:
                #     assignment_dict["due_date"] = assignment_dict["due_date"].strftime('%Y-%m-%dT%H:%M:%SZ')

                statuses2.append([status["assignment_id"], status["assignment_group_title"],  assignment_dict])

        return statuses2

    def parse_assignment_groups(self, assignment_statuses):
        assignment_groups = []

        for assignment_status in assignment_statuses:
            assignment_group = [assignment_status[1], assignment_status[2]["assignment_group_id"]]

            if assignment_group not in assignment_groups:
                assignment_groups.append(assignment_group)

        assignment_groups = sorted(assignment_groups)

        # Move the blank one to the end.
        if len(assignment_groups) > 0 and assignment_groups[0][0] == "":
            del assignment_groups[0]
            assignment_groups.append(["", -1])

        return assignment_groups

    def get_assignment_groups(self, course_id):
        sql = '''
SELECT title, assignment_group_id
FROM assignment_groups
WHERE course_id = ?
ORDER BY title'''

        assignment_groups = []

        for row in self.fetchall(sql, (course_id, )):
            assignment_groups.append([row["title"], row["assignment_group_id"]])

        return assignment_groups

    def add_assignment_group(self, course_id, assignment_group_title):
        sql = '''
INSERT INTO assignment_groups (course_id, title)
VALUES (?, ?)
'''
        self.execute(sql, (course_id, assignment_group_title))
    
    def remove_assignment_group(self, course_id, assignment_group_id):
        sql1 = '''
DELETE FROM assignment_groups
WHERE course_id = ?
  AND assignment_group_id = ?
'''
        params = [(course_id, assignment_group_id)]

        sql2 = '''
UPDATE assignments
SET assignment_group_id = NULL
WHERE course_id = ?
  AND assignment_group_id = ?
'''

        params.append((course_id, assignment_group_id))

        self.execute_multiple([sql1, sql2], params)

    # Gets the number of submissions a student has made for each exercise
    # in an assignment and whether or not they have passed the exercise.
    # TODO: Pass basics info into this function?
    def get_exercise_statuses(self, course_id, assignment_id, user_id, show_hidden=False, nice_sort=True):
        # This happens when you are creating a new assignment.
        if not assignment_id:
            return []

        sql = self.scores_statuses_temp_tables_sql + '''
SELECT
  user_id,
  id,
  title,
  visible,
  enable_pair_programming,
  MAX(num_submissions) AS num_submissions,
  completed,
  in_progress,
  score,
  weight,
  is_multiple_choice
FROM (
  SELECT
    es.user_id,
    es.exercise_id as id,
    e.title,
    e.visible,
    e.enable_pair_programming,
    es.num_submissions,
    es.completed,
    es.in_progress,
    esw.score,
    e.weight,
    e.is_multiple_choice
  FROM exercise_statuses es
  INNER JOIN exercise_scores_weights esw
    ON es.assignment_id = esw.assignment_id
    AND es.exercise_id = esw.exercise_id
    AND es.user_id = esw.user_id
  INNER JOIN valid_exercises e
    ON es.assignment_id = e.assignment_id
    AND es.exercise_id = e.exercise_id

  UNION

  SELECT
    NULL AS user_id,
    exercise_id AS id,
    title,
    visible,
    enable_pair_programming,
    0 AS num_submissions,
    0 AS completed,
    0 AS in_progress,
    0 AS score,
    weight,
    is_multiple_choice
  FROM valid_exercises
)
GROUP by id
'''

        statuses = []
        for row in self.fetchall(sql, (course_id, assignment_id, None, user_id,)):
            if row["visible"] or show_hidden:
                statuses.append(dict(row))

        if nice_sort:
            statuses = sort_list_of_dicts_nicely(statuses, ["title", "id"])

        statuses2 = []

        for status in statuses:
            statuses2.append([status["id"], status])

        return statuses2

    ## Calculates the average score across all students for each assignment in a course, as well as the number of students who have completed each assignment.
    def get_assignment_summary_scores(self, course_id):
        sql = self.scores_statuses_temp_tables_sql + '''
SELECT
  assignment_id,
  title,
  visible,
  MAX(num_students) AS num_students,
  num_students_completed,
  start_date,
  due_date,
  avg_score
FROM (
  SELECT
    sts.assignment_id,
    a.title,
    a.visible,
    COUNT(sts.user_id) AS num_students,
    SUM(sts.completed) AS num_students_completed,
    sts.start_date,
    sts.due_date,
    AVG(scr.score) AS avg_score
  FROM assignment_statuses sts
  INNER JOIN assignment_scores scr
    ON sts.assignment_id = scr.assignment_id
    AND sts.user_id = scr.user_id
  INNER JOIN valid_assignments a
    ON sts.assignment_id = a.assignment_id
  GROUP BY sts.assignment_id

  UNION

  SELECT
    assignment_id,
    title,
    visible,
    0 AS num_students,
    0 AS num_students_completed,
    NULL AS start_date,
    NULL AS due_date,
    0 AS avg_score
  FROM valid_assignments
)
GROUP BY assignment_id
'''

        assignment_scores = {}

        for row in self.fetchall(sql, (course_id, None, None, None)):
            assignment_scores[row["assignment_id"]] = dict(row)

        return assignment_scores

    ## Calculates the average score across all students for each exercise in an assignment,
    ## as well as the number of students who have completed each exercise.
    def get_exercise_summary_scores(self, course_basics, assignment_basics):
        sql = self.scores_statuses_temp_tables_sql + '''
SELECT
  id,
  title,
  visible,
  MAX(num_students) AS num_students,
  num_students_completed,
  score
FROM (
  SELECT
    sts.exercise_id AS id,
    e.title,
    e.visible,
    COUNT(sts.user_id) AS num_students,
    SUM(sts.completed) AS num_students_completed,
    AVG(esw.score) AS score
  FROM exercise_statuses sts
  INNER JOIN exercise_scores_weights esw
    ON sts.exercise_id = esw.exercise_id
    AND sts.user_id = esw.user_id
  INNER JOIN valid_exercises e
    ON sts.exercise_id = e.exercise_id
  GROUP BY sts.exercise_id

  UNION

  SELECT
    exercise_id AS id,
    title,
    visible,
    0 AS num_students,
    0 AS num_students_completed,
    0 AS score
  FROM valid_exercises
)
GROUP BY id
'''

        scores_dict = {}
        for row in self.fetchall(sql, (course_basics["id"], assignment_basics["id"], None, None)):
            scores_dict[row["id"]] = dict(row)

        return scores_dict

    # Gets all users who have submitted on a particular assignment and creates a list of their average scores for the assignment.
    def get_assignment_scores(self, course_basics, assignment_basics):
        sql = self.scores_statuses_temp_tables_sql + '''
SELECT
  u.user_id AS id,
  u.name,
  scr.score,
  sts.num_completed,
  ane.num_exercises,
  sts.last_submission_timestamp,
  sts.num_times_pair_programmed
FROM assignment_statuses sts
INNER JOIN assignment_scores scr
  ON sts.assignment_id = scr.assignment_id
  AND sts.user_id = scr.user_id
INNER JOIN valid_users u
  ON sts.user_id = u.user_id
INNER JOIN assignments_num_exercises ane
  ON sts.assignment_id = ane.assignment_id
ORDER BY u.name
'''

        scores_dict_list = []
        total_times_pair_programmed = 0

        for row in self.fetchall(sql, (course_basics["id"], assignment_basics["id"], None, None)):
            data = dict(row)
            data["last_submission_timestamp"] = localize_datetime(convert_string_to_datetime(data["last_submission_timestamp"]))
            scores_dict_list.append([data["id"], data])

            total_times_pair_programmed += data["num_times_pair_programmed"]                

        return scores_dict_list, total_times_pair_programmed

    # Get score for each assignment for a particular student.
    def get_student_assignment_scores(self, course_id, user_id):
        sql = self.scores_statuses_temp_tables_sql + '''
SELECT
  a.assignment_id,
  a.title,
  scr.score,
  sts.num_completed,
  ane.num_exercises,
  sts.last_submission_timestamp,
  sts.num_times_pair_programmed
FROM assignment_statuses sts
INNER JOIN assignment_scores scr
  ON sts.assignment_id = scr.assignment_id
  AND sts.user_id = scr.user_id
INNER JOIN valid_assignments a
  ON sts.assignment_id = a.assignment_id
INNER JOIN assignments_num_exercises ane
  ON sts.assignment_id = ane.assignment_id
ORDER BY a.title
'''

        scores = []

        for row in self.fetchall(sql, (course_id, None, None, user_id, )):
            data = dict(row)
            data["last_submission_timestamp"] = localize_datetime(convert_string_to_datetime(data["last_submission_timestamp"]))
            scores.append([row["assignment_id"], data])

        return scores

    def get_exercise_scores(self, course_id, assignment_id, exercise_id):
        scores = []

        sql = self.scores_statuses_temp_tables_sql + '''
SELECT
  u.name,
  u.user_id,
  sts.num_submissions,
  scr.score,
  sts.last_submission_timestamp,
  sts.pair_programmed
FROM exercise_statuses sts
INNER JOIN exercise_scores_weights scr
  ON sts.assignment_id = scr.assignment_id
  AND sts.user_id = scr.user_id
INNER JOIN valid_users u
  ON sts.user_id = u.user_id
ORDER BY u.name
'''

        for row in self.fetchall(sql, (course_id, assignment_id, exercise_id, None, )):
            data = dict(row)
            data["last_submission_timestamp"] = localize_datetime(convert_string_to_datetime(data["last_submission_timestamp"]))
            scores.append([row["user_id"], data])

        return scores

    def get_student_exercise_score(self, course_id, assignment_id, exercise_id, user_id):
        sql = self.scores_statuses_temp_tables_sql + '''
SELECT scr.score
FROM exercise_scores_weights scr
'''

        result = self.fetchone(sql, (course_id, assignment_id, exercise_id, user_id, ))

        if result:
          return result["score"]
        return 0

    def save_exercise_score(self, course_id, assignment_id, exercise_id, user_id, score):
        # We only update the score if it's higher than what was there previously. We also account for the scenario where it is their first submission.
        sql = '''WITH user_scores AS (
                   SELECT score
		               FROM scores
		               WHERE course_id = ?
		                 AND assignment_id = ?
				             AND exercise_id = ?
				             AND user_id = ?

		               UNION
		
		               SELECT 0
                 )

                 INSERT OR REPLACE INTO scores (course_id, assignment_id, exercise_id, user_id, score)
                 SELECT ?, ?, ?, ?, ?
                 WHERE ? >= (SELECT MAX(score) FROM user_scores)'''

        self.execute(sql, (course_id, assignment_id, exercise_id, user_id, course_id, assignment_id, exercise_id, user_id, score, score))

    def get_submissions(self, course_id, assignment_id, exercise_id, user_id, exercise_details):
        sql = '''
SELECT
  o.submission_id,
  t.title,
  o.txt_output,
  o.jpg_output
FROM test_outputs o
INNER JOIN tests t
  ON o.test_id = t.test_id
INNER JOIN submissions s
  ON o.submission_id = s.submission_id
LEFT JOIN users u
  ON s.partner_id = u.user_id
WHERE t.course_id = ?
  AND t.assignment_id = ?
  AND t.exercise_id = ?
  AND s.user_id = ?'''

        test_outputs = {}
        for row in self.fetchall(sql, (int(course_id), int(assignment_id), int(exercise_id), user_id,)):
            submission_id = row["submission_id"]
            test_title = row["title"]

            if not submission_id in test_outputs:
                test_outputs[submission_id] = {}

            if not test_title in test_outputs[submission_id]:
                test_outputs[submission_id][test_title] = {}

            test_outputs[submission_id][test_title]["txt_output"] = row["txt_output"]
            test_outputs[submission_id][test_title]["jpg_output"] = row["jpg_output"]
            test_outputs[submission_id][test_title]["txt_output_formatted"] = format_output_as_html(row["txt_output"])

        sql = self.scores_statuses_temp_tables_sql + '''
SELECT su.submission_id AS id,
       su.code,
       (su.passed OR e.back_end = 'multiple_choice') AS completed,
       su.passed,
       su.date AS submission_timestamp,
       sc.score,
       u.name AS partner_name
FROM submissions su
INNER JOIN exercises e
  ON su.course_id = e.course_id
  AND su.assignment_id = e.assignment_id
  AND su.exercise_id
INNER JOIN scores sc
  ON su.course_id = sc.course_id
  AND su.assignment_id = sc.assignment_id
  AND su.exercise_id = sc.exercise_id
  AND su.user_id = sc.user_id
LEFT JOIN users u
  ON su.partner_id = u.user_id
WHERE su.course_id = ?
  AND su.assignment_id = ?
  AND su.exercise_id = ?
  AND su.user_id = ?

UNION

SELECT -1, presubmission as code, FALSE, 0, NULL, 0, NULL
FROM presubmissions
WHERE course_id = ?
  AND assignment_id = ?
  AND exercise_id = ?
  AND user_id = ?

ORDER BY submission_timestamp
'''

#         sql = self.scores_statuses_temp_tables_sql + '''
# SELECT
#   s.submission_id AS id,
#   s.code,
#   s.completed,
#   s.submission_timestamp,
#   esw.score,
#   u2.name AS partner_name
# FROM valid_submissions s
# INNER JOIN exercise_scores_weights esw
#   ON s.exercise_id = esw.exercise_id
#   AND s.user_id = esw.user_id
# LEFT JOIN users u2
#   ON s.partner_id = u2.user_id

# UNION

# SELECT
#   -1 AS id,
#   p.code,
#   0 AS completed,
#   NULL AS submission_timestamp,
#   0 AS score,
#   NULL AS partner_name
# FROM presubmissions p
# INNER JOIN valid_assignments a
#   ON p.assignment_id = a.assignment_id
# INNER JOIN valid_exercises e
#   ON p.exercise_id = e.exercise_id
# INNER JOIN valid_users u
#   ON p.user_id = u.user_id
# WHERE p.course_id = (SELECT course_id FROM variables)

# ORDER BY submission_timestamp
# '''

        presubmission = None
        submissions = []
        has_passed = False

        for row in self.fetchall(sql, (course_id, assignment_id, exercise_id, user_id, course_id, assignment_id, exercise_id, user_id, course_id, assignment_id, exercise_id, user_id)):
            submission_test_outputs = {}

            if row["id"] == -1:
                presubmission = row["code"]
            else:
                submission = dict(row)
                submission["submission_timestamp"] = localize_datetime(submission["submission_timestamp"])

                if submission["id"] in test_outputs:
                    submission_test_outputs = test_outputs[submission["id"]]

                    check_test_outputs(exercise_details, submission_test_outputs)
                    sanitize_test_outputs(exercise_details, submission_test_outputs)

                submission["test_outputs"] = submission_test_outputs
                submissions.append(submission)

                if submission["completed"] == True:
                    has_passed = True

        return presubmission, submissions, has_passed

    async def get_num_submissions(self, course_id, assignment_id, exercise_id, user_id):
        sql = self.scores_statuses_temp_tables_sql + '''
SELECT COUNT(*) AS count
FROM valid_submissions'''

        return self.fetchone(sql, (course_id, assignment_id, exercise_id, user_id, ))["count"]
    
    async def get_num_course_submissions(self, course_id):
        sql = self.scores_statuses_temp_tables_sql + '''
SELECT COUNT(*) AS count
FROM valid_submissions'''

        return self.fetchone(sql, (course_id, None, None, None))["count"]

    def get_most_recent_submission_code(self, course_id, assignment_id, exercise_id, user_id, must_have_passed=True):
        sql = '''SELECT code
                 FROM submissions
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND exercise_id = ?
                   AND user_id = ?'''
        
        if must_have_passed:
            sql += "AND passed = ?"
            args = (course_id, assignment_id, exercise_id, user_id, 1)
        else:
            args = (course_id, assignment_id, exercise_id, user_id)

        sql += '''ORDER BY date DESC
                  LIMIT 1'''

        result = self.fetchone(sql, args)

#         sql = self.scores_statuses_temp_tables_sql + '''
# SELECT code
# FROM latest_completed_submissions
# '''

        # result = self.fetchone(sql, (course_id, assignment_id, exercise_id, user_id,))

        if result and result["code"]:
            return result["code"]
        else:
            return ""

    def get_peer_most_recent_submission_code(self, course_id, assignment_id, exercise_id, user_id):
        sql = self.scores_statuses_temp_tables_sql + '''
SELECT user_id, code
FROM latest_completed_submissions
WHERE user_id != ?
  AND (partner_id != ? OR partner_id IS NULL)
ORDER BY user_id
  '''

        peer_code_dict = {}
        for row in self.fetchall(sql, (course_id, assignment_id, exercise_id, None, user_id, user_id)):
            peer_code_dict[row["user_id"]] = row["code"]

        # For privacy reasons, only show peers' solutions if at least three have submitted.
        if len(peer_code_dict) <= 3:
            return ""

        peer_ids = list(peer_code_dict.keys())
        random.shuffle(peer_ids)

        return peer_code_dict[peer_ids[0]]

    # FYI: This retrieves the latest submission and score for each student for a given exercise.
    def get_exercise_submissions(self, course_id, assignment_id, exercise_id):
        exercise_submissions = []

        sql = self.scores_statuses_temp_tables_sql + '''
SELECT
  s.user_id AS student_id,
  u.name AS student_name,
  s.code,
  s.submission_timestamp AS submission_timestamp,
  s.partner_id,
  u2.name AS partner_name,
  esw.score,
  sts.completed
FROM latest_submissions s
INNER JOIN exercise_statuses sts
  ON s.exercise_id = sts.exercise_id
  AND s.user_id = sts.user_id
INNER JOIN exercise_scores_weights esw
  ON s.exercise_id = esw.exercise_id
  AND s.user_id = esw.user_id
INNER JOIN valid_users u
  ON s.user_id = u.user_id
LEFT JOIN valid_users u2
  ON u2.user_id = s.partner_id
ORDER BY student_name
'''

        for row in self.fetchall(sql, (course_id, assignment_id, exercise_id, None, )):
            data = dict(row)
            data["submission_timestamp"] = localize_datetime(convert_string_to_datetime(data["submission_timestamp"]))
            exercise_submissions.append([row["student_id"], data])

        return exercise_submissions

    def specify_course_basics(self, course_basics, title, visible):
        course_basics["title"] = title
        course_basics["visible"] = visible

    def specify_course_details(self, course_details, introduction, passcode, email_address, highlighted, allow_students_download_submissions, virtual_assistant_config, date_created, date_updated):
        course_details["introduction"] = introduction
        course_details["passcode"] = passcode
        course_details["email_address"] = email_address
        course_details["highlighted"] = highlighted
        course_details["allow_students_download_submissions"] = allow_students_download_submissions
        course_details["virtual_assistant_config"] = virtual_assistant_config
        course_details["date_updated"] = date_updated

        if course_details["date_created"]:
            course_details["date_created"] = date_created
        else:
            course_details["date_created"] = date_updated

    def get_course_basics(self, course_id):
        null_course = {"id": "", "title": "", "visible": True, "exists": False}

        if not course_id:
            return null_course

        sql = '''SELECT course_id, title, visible
                 FROM courses
                 WHERE course_id = ?'''

        row = self.fetchone(sql, (int(course_id),))

        if not row:
            return null_course

        return {"id": row["course_id"], "title": row["title"], "visible": bool(row["visible"]), "exists": True}
    
    def get_assignments(self, course_basics, show_hidden=True):
        sql = '''SELECT a.assignment_id as id, a.title, a.start_date, a.due_date, a.visible, IFNULL(ag.assignment_group_id, '') AS assignment_group_id, IFNULL(ag.title, '') AS assignment_group_title
                 FROM assignments a
                 LEFT JOIN assignment_groups ag
                     ON a.course_id = ag.course_id AND a.assignment_group_id = ag.assignment_group_id
                 WHERE a.course_id = ?
                 ORDER BY a.title'''

        # We initially structure it this way to make sorting easier.
        assignments = []
        for row in self.fetchall(sql, (course_basics["id"],)):
            if row["visible"] or show_hidden:
                assignment = dict(row)

                assignment["start_date"] = localize_datetime(assignment["start_date"])
                assignment["due_date"] =  localize_datetime(assignment["due_date"])
                assignments.append(assignment)

        assignments = sort_list_of_dicts_nicely(assignments, ["assignment_group_title",  "title", "id"])

        # We restructure it to be consistent with courses and exercises
        assignments2 = []
        for assignment in assignments:
            assignments2.append([assignment["id"], assignment["assignment_group_title"], assignment])

        return assignments2
    
    def get_secure_assignments(self, course_id, candidate_assignment_ids=None):
        sql = '''SELECT assignment_id, title, require_security_codes
                 FROM assignments a
                 WHERE course_id = ?
                    AND visible = 1
                    AND require_security_codes != 0
                 ORDER by title'''

        assignments_dict = {}
        for row in self.fetchall(sql, (course_id,)):
            assignment_id = row["assignment_id"]

            if not candidate_assignment_ids or assignment_id in candidate_assignment_ids:
              assignments_dict[row["title"]] = {"id": assignment_id, "require_security_codes": row["require_security_codes"]}

        return assignments_dict
    
    def save_security_codes(self, course_id, selected_assignment_ids, overwrite_existing, student_count, make_distinct):
        characters_per_segment = 4
        num_segments = 3
        delimiter = " "

        # This will be used when make_distinct is True.
        security_code = generate_unique_id(characters_per_segment, num_segments, delimiter)

        sql_statements = []
        param_lists = []
        assignment_security_code_dict = {}

        sql_delete = '''DELETE FROM security_codes
                        WHERE course_id = ?
                          AND assignment_id = ?'''

        sql_insert = '''INSERT INTO security_codes (course_id, assignment_id, security_code, confirmation_code)
                        VALUES (?, ?, ?, ?)'''

        for assignment_id in selected_assignment_ids:
            assignment_security_code_dict[assignment_id] = []

            existing_security_codes = self.get_security_codes(course_id, assignment_id)

            if len(existing_security_codes) == 0 or overwrite_existing:
                sql_statements.append(sql_delete)
                param_lists.append([course_id, assignment_id])

                for i in range(student_count):
                    if make_distinct:
                        security_code = generate_unique_id(characters_per_segment, num_segments, delimiter)
                    
                    confirmation_code = generate_unique_id(4, 1)

                    sql_statements.append(sql_insert)
                    param_lists.append([course_id, assignment_id, security_code.replace(delimiter, ""), confirmation_code])

                    assignment_security_code_dict[assignment_id].append([security_code, confirmation_code])
            else:
                for x in existing_security_codes:
                  assignment_security_code_dict[assignment_id].append([split_str_by_positions(x["security_code"], characters_per_segment, delimiter), x["confirmation_code"]])

        self.execute_multiple(sql_statements, param_lists)

        return assignment_security_code_dict

    def verify_security_code(self, course_id, assignment_id, security_code, student_id):
        # 1. Make sure the user has not already verified.
        # 2. Get the rowid associated with the row to insert. The instructor can specify that the same security code is used for all students, so we have to do it this way.
        # 3. Update the identified row.
        # 4. Because these are executed in 2 separate steps, it is possible that the row could be updated for a different user between the two steps, so we need to check that.

        if self.has_verified_security_code(course_id, assignment_id, student_id):
            return -1

        sql = '''
            WITH RowToUpdate AS (
                SELECT rowid
                FROM security_codes
                WHERE course_id = ?
                  AND assignment_id = ?
                  AND security_code = ?
                AND student_id IS NULL
                LIMIT 1
            )

            UPDATE security_codes
            SET student_id = ?
            WHERE rowid = (SELECT rowid FROM RowToUpdate)
              AND student_id IS NULL'''

        self.execute(sql, (course_id, assignment_id, security_code, student_id))

        if not self.has_verified_security_code(course_id, assignment_id, student_id):
            self.execute(sql, (course_id, assignment_id, security_code, student_id))

        return self.has_verified_security_code(course_id, assignment_id, student_id) is not None
    
    def has_verified_security_code(self, course_id, assignment_id, student_id):
        sql = '''SELECT confirmation_code
                 FROM security_codes
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND student_id = ?'''

        result = self.fetchone(sql, (course_id, assignment_id, student_id))
        
        if result:
            return result["confirmation_code"]

    def get_security_codes(self, course_id, assignment_id):
        sql = '''SELECT sc.security_code, sc.confirmation_code, IFNULL(sc.student_id, '-') AS student_id, IFNULL(u.name, '-') as student_name
                 FROM security_codes sc
                 LEFT JOIN users u
                   ON sc.student_id = u.user_id
                 WHERE sc.course_id = ?
                   AND sc.assignment_id = ?
                 ORDER BY CASE
                            WHEN u.name IS NULL THEN 1 
                            ELSE 0
                          END, u.name, sc.security_code'''

        results = []
        for row in self.fetchall(sql, (course_id, assignment_id)):
            results.append(dict(row))
        
        return results

    def get_assignment_basics(self, course_basics, assignment_id):
        if not assignment_id:
            return {"id": "", "title": "", "visible": True, "exists": False, "course": course_basics}

        sql = '''SELECT assignment_id, title, visible
                 FROM assignments
                 WHERE course_id = ?
                   AND assignment_id = ?'''

        row = self.fetchone(sql, (int(course_basics['id']), assignment_id,))
        if row is None:
            return {"id": "", "title": "", "visible": True, "exists": False, "course": course_basics}
        else:
            return {"id": row["assignment_id"], "title": row["title"], "visible": bool(row["visible"]), "exists": True, "course": course_basics}

    def get_exercise_basics(self, course_basics, assignment_basics, exercise_id):
        if not exercise_id:
            return {"id": "", "title": "", "visible": True, "exists": False, "assignment": assignment_basics}

        sql = '''SELECT exercise_id, title, visible, enable_pair_programming
                 FROM exercises
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND exercise_id = ?'''

        row = self.fetchone(sql, (course_basics['id'], assignment_basics['id'], exercise_id,))
        if row is None:
            return {"enable_pair_programming": False, "id": "", "title": "", "visible": True, "exists": False, "assignment": assignment_basics}
        else:
            return {"enable_pair_programming": row["enable_pair_programming"], "id": row["exercise_id"], "title": row["title"], "visible": bool(row["visible"]), "exists": True, "assignment": assignment_basics}

    def get_next_prev_exercises(self, course_id, assignment_id, exercise, exercises):
        prev_exercise = None
        next_exercise = None

        if len(exercises) > 0 and exercise:
            this_exercise = [i for i in range(len(exercises)) if exercises[i][0] == int(exercise)]
            if len(this_exercise) > 0:
                this_exercise_index = [i for i in range(len(exercises)) if exercises[i][0] == int(exercise)][0]

                if len(exercises) >= 2 and this_exercise_index != 0:
                    prev_exercise = exercises[this_exercise_index - 1][1]

                if len(exercises) >= 2 and this_exercise_index != (len(exercises) - 1):
                    next_exercise = exercises[this_exercise_index + 1][1]

        return {"previous": prev_exercise, "next": next_exercise}

    def delete_old_presubmissions(self):
        sql = '''DELETE
                 FROM presubmissions
                 WHERE date_updated < datetime('now', '-12 months')'''

        self.execute(sql)

    def get_presubmission(self, course_id, assignment_id, exercise_id, user_id):
        sql = '''SELECT code
                 FROM presubmissions
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND exercise_id = ?
                   AND user_id = ?'''

        row = self.fetchone(sql, (int(course_id), int(assignment_id), int(exercise_id), user_id))

        return row["code"] if row else None

    def get_course_details(self, course_id):
        null_course = {"introduction": "", "passcode": None, "date_created": None, "date_updated": None, "email_address": "", "highlighted": False, "allow_students_download_submissions": False, "virtual_assistant_config": None}

        if not course_id:
            return null_course

        sql = '''SELECT introduction, passcode, date_created, date_updated, email_address, highlighted, allow_students_download_submissions, virtual_assistant_config
                 FROM courses
                 WHERE course_id = ?'''

        row = self.fetchone(sql, (course_id,))

        if not row:
            return null_course

        course_details = {"introduction": row["introduction"], "passcode": row["passcode"], "date_created": row["date_created"], "date_updated": row["date_updated"], "email_address": row["email_address"], "highlighted": row["highlighted"], "allow_students_download_submissions": row["allow_students_download_submissions"], "virtual_assistant_config": row["virtual_assistant_config"]}

        if course_details["virtual_assistant_config"]:
            course_details["virtual_assistant_config"] = load_yaml_dict(course_details["virtual_assistant_config"])

        sql = '''SELECT COUNT(*) > 0 AS yes
                 FROM assignments
                 WHERE course_id = ?
                   AND restrict_other_assignments = 1'''

        course_details["check_for_restrict_other_assignments"] = bool(self.fetchone(sql, (course_id, ))["yes"])

        return course_details

    def get_assignment_details(self, course_basics, assignment_id):
        null_assignment = {"introduction": "", "date_created": None, "date_updated": None, "start_date": None, "due_date": None, "allow_late": False, "late_percent": None, "view_answer_late": False, "has_timer": 0, "hour_timer": None, "minute_timer": None, "restrict_other_assignments": False, "allowed_ip_addresses": None, "allowed_external_urls": "", "show_run_button": True, "custom_scoring": "", "require_security_codes": 0, "prerequisite_assignment_ids": [], "student_early_exceptions": [], "student_late_exceptions": [], "student_timer_exceptions": {}, "support_questions": False, "use_virtual_assistant": 0, "assignment_group_id": None}

        if not assignment_id:
            return null_assignment

        sql = '''SELECT a.introduction, a.date_created, a.date_updated, a.start_date, a.due_date, a.allow_late, a.late_percent, a.view_answer_late, a.allowed_ip_addresses, a.allowed_external_urls, a.show_run_button, a.custom_scoring, a.require_security_codes, a.support_questions, a.use_virtual_assistant, a.has_timer, a.hour_timer, a.minute_timer, a.restrict_other_assignments, ag.assignment_group_id
                 FROM assignments a
                 LEFT JOIN assignment_groups ag
                   ON a.course_id = ag.course_id
                   AND a.assignment_group_id = ag.assignment_group_id
                 WHERE a.course_id = ?
                   AND a.assignment_id = ?'''

        row = self.fetchone(sql, (course_basics['id'], assignment_id,))

        if not row:
            return null_assignment

        assignment_dict = {"introduction": row["introduction"], "date_created": row["date_created"], "date_updated": row["date_updated"], "start_date":  localize_datetime(row["start_date"]), "due_date":  localize_datetime(row["due_date"]), "allow_late": row["allow_late"], "late_percent": row["late_percent"], "view_answer_late": row["view_answer_late"], "allowed_ip_addresses": row["allowed_ip_addresses"], "allowed_external_urls": row["allowed_external_urls"], "show_run_button": row["show_run_button"], "custom_scoring": row["custom_scoring"] if row["custom_scoring"] else "", "require_security_codes": row["require_security_codes"], "prerequisite_assignment_ids": self.get_prerequisite_assignment_ids(course_basics['id'], assignment_id), "student_early_exceptions": self.get_student_early_exceptions(course_basics['id'], assignment_id), "student_late_exceptions": self.get_student_late_exceptions(course_basics['id'], assignment_id), "student_timer_exceptions": self.get_student_timer_exceptions(row["has_timer"], course_basics['id'], assignment_id), "support_questions": row["support_questions"], "use_virtual_assistant": row["use_virtual_assistant"], "has_timer": row["has_timer"], "hour_timer": row["hour_timer"], "minute_timer": row["minute_timer"], "restrict_other_assignments": row["restrict_other_assignments"], "assignment_group_id": row["assignment_group_id"]}

        if assignment_dict["allowed_ip_addresses"]:
            assignment_dict["allowed_ip_addresses_list"] = assignment_dict["allowed_ip_addresses"].split("\n")

        return assignment_dict

    def get_exercise_details(self, course_basics, assignment_basics, exercise_id):
        null_exercise = {"instructions": "", "back_end": "python", "output_type": "txt", "allow_any_response": False, "solution_code": "", "solution_description": "", "hint": "", "max_submissions": 0, "starter_code": "", "credit": "", "data_files": [], "what_students_see_after_success": 1, "date_created": None, "date_updated": None, "enable_pair_programming": False, "verification_code": "", "weight": 1.0, "min_solution_length": 1, "max_solution_length": 10000, "tests": {}}

        if not exercise_id:
            return null_exercise

        sql = '''SELECT instructions, back_end, output_type, allow_any_response, solution_code, solution_description, hint, max_submissions, starter_code, credit, data_files, what_students_see_after_success, date_created, date_updated, enable_pair_programming, verification_code, weight, min_solution_length, max_solution_length
                 FROM exercises
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND exercise_id = ?'''

        row = self.fetchone(sql, (course_basics['id'], assignment_basics['id'], exercise_id,))

        if not row:
            return null_exercise

        exercise_dict = {"instructions": row["instructions"], "back_end": row["back_end"], "output_type": row["output_type"], "allow_any_response": row["allow_any_response"], "solution_code": row["solution_code"], "solution_description": row["solution_description"], "hint": row["hint"], "max_submissions": row["max_submissions"], "starter_code": row["starter_code"], "credit": row["credit"], "data_files": ujson.loads(row["data_files"]), "what_students_see_after_success": row["what_students_see_after_success"], "date_created": row["date_created"], "date_updated": row["date_updated"], "enable_pair_programming": row["enable_pair_programming"], "verification_code": row["verification_code"], "weight": row["weight"], "min_solution_length": row["min_solution_length"], "max_solution_length": row["max_solution_length"], "tests": {}}

        # For multiple-choice questions, we store the sandbox back end in this field.
        if exercise_dict["back_end"] == "multiple_choice" and exercise_dict["starter_code"] == "None":
            exercise_dict["starter_code"] = ""

        sql = '''SELECT test_id,
                   title,
                   before_code,
                   after_code,
                   instructions,
                   can_see_test_code,
                   can_see_expected_output,
                   can_see_code_output,
                   txt_output,
                   jpg_output
                 FROM tests
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND exercise_id = ?'''

        tests = self.fetchall(sql, (course_basics['id'], assignment_basics['id'], exercise_id,))

        for test in tests:
            exercise_dict["tests"][test["title"]] = {"test_id": test["test_id"], "before_code": test["before_code"], "after_code": test["after_code"], "instructions": test["instructions"], "can_see_test_code": test["can_see_test_code"], "can_see_expected_output": test["can_see_expected_output"], "can_see_code_output": test["can_see_code_output"], "txt_output": test["txt_output"], "jpg_output": test["jpg_output"]}

        return exercise_dict

    def get_prerequisite_assignment_ids(self, course_id, assignment_id):
        prerequisite_assignment_ids = []

        sql = '''SELECT pa.prerequisite_assignment_id
                 FROM prerequisite_assignments pa
                 INNER JOIN assignments a
                   ON pa.course_id = a.course_id
                   AND pa.assignment_id = a.assignment_id
                 WHERE pa.course_id = ?
                   AND pa.assignment_id = ?
                 ORDER BY a.title'''
        
        for row in self.fetchall(sql, (course_id, assignment_id)):
            prerequisite_assignment_ids.append(row["prerequisite_assignment_id"])

        return prerequisite_assignment_ids

    def get_assignments_prerequiring_this_assignment(self, course_id, assignment_id):
        assignment_ids = []

        sql = '''SELECT assignment_id
                 FROM prerequisite_assignments
                 WHERE course_id = ?
                   AND prerequisite_assignment_id = ?'''
        
        for row in self.fetchall(sql, (course_id, assignment_id)):
            assignment_ids.append(row["assignment_id"])

        return assignment_ids

    def get_student_early_exceptions(self, course_id, assignment_id):
        users = []

        sql = '''SELECT user_id
                FROM assignment_early_exceptions
                WHERE course_id = ?
                  AND assignment_id = ?'''

        for row in self.fetchall(sql, (course_id, assignment_id, )):
            users.append(row["user_id"])

        return users

    def get_student_late_exceptions(self, course_id, assignment_id):
        users = []

        sql = '''SELECT user_id
                FROM assignment_late_exceptions
                WHERE course_id = ?
                  AND assignment_id = ?'''

        for row in self.fetchall(sql, (course_id, assignment_id, )):
            users.append(row["user_id"])

        return users

    def student_has_early_exception(self, course_id, assignment_id, user_id):
        sql = '''SELECT COUNT(*) > 0 AS has_exception
                FROM assignment_early_exceptions
                WHERE course_id = ?
                  AND assignment_id = ?
                  AND user_id = ?'''

        return self.fetchone(sql, (course_id, assignment_id, user_id))["has_exception"]

    def student_has_late_exception(self, course_id, assignment_id, user_id):
        sql = '''SELECT COUNT(*) > 0 AS has_exception
                FROM assignment_late_exceptions
                WHERE course_id = ?
                  AND assignment_id = ?
                  AND user_id = ?'''

        return self.fetchone(sql, (course_id, assignment_id, user_id))["has_exception"]

    def get_student_timer_exceptions(self, has_timer, course_id, assignment_id):
        exceptions = {}

        if has_timer:
            sql = '''SELECT user_id, hour_timer, minute_timer
                    FROM assignment_timer_exceptions
                    WHERE course_id = ?
                      AND assignment_id = ?'''
            
            for row in self.fetchall(sql, (course_id, assignment_id, )):
                exceptions[row["user_id"]] = [row["hour_timer"], row["minute_timer"]]

        return exceptions

    def get_log_table_contents(self, file_path, year="No filter", month="No filter", day="No filter"):
        new_dict = {}
        line_num = 1
        with gzip.open(file_path) as read_file:
            header = read_file.readline()
            for line in read_file:
                line_items = line.decode().rstrip("\n").split("\t")

                #Get ids to create links to each course, assignment, and exercise in the table
                course_id = line_items[1]
                assignment_id = line_items[2]
                exercise_id = line_items[3]

                line_items[6] = f"<a href='/course/{course_id}'>{line_items[6]}</a>"
                line_items[7] = f"<a href='/assignment/{course_id}/{assignment_id}'>{line_items[7]}</a>"
                line_items[8] = f"<a href='/exercise/{course_id}/{assignment_id}/{exercise_id}'>{line_items[8]}</a>"

                line_items = [line_items[0][:2], line_items[0][2:4], line_items[0][4:6], line_items[0][6:]] + line_items[4:]

                new_dict[line_num] = line_items
                line_num += 1

        # Filter by date.
        year_dict = {}
        month_dict = {}
        day_dict = {}

        for key, line in new_dict.items():
            if year == "No filter" or line[0] == year:
                year_dict[key] = line
        for key, line in year_dict.items():
            if month == "No filter" or line[1] == month:
                month_dict[key] = line
        for key, line in month_dict.items():
            if day == "No filter" or line[2] == day:
                day_dict[key] = line

        return day_dict

    def sort_nested_list(self, nested_list, key="title"):
        l_dict = {}
        for row in nested_list:
            l_dict[row[1][key]] = row

        return [l_dict[key] for key in sort_nicely(l_dict)]

    def save_course(self, course_basics, course_details):
        if course_basics["exists"]:
            sql = '''UPDATE courses
                     SET title = ?, visible = ?, introduction = ?, passcode = ?, email_address = ?, highlighted = ?,  allow_students_download_submissions = ?, virtual_assistant_config = ?, date_updated = ?
                     WHERE course_id = ?'''

            self.execute(sql, [course_basics["title"], course_basics["visible"], course_details["introduction"], course_details["passcode"], course_details["email_address"], course_details["highlighted"], course_details["allow_students_download_submissions"], course_details["virtual_assistant_config"], course_details["date_updated"], course_basics["id"]])

            self.update_when_content_updated(course_basics["id"])
        else:
            sql = '''INSERT INTO courses (title, visible, introduction, passcode, email_address, highlighted, allow_students_download_submissions, virtual_assistant_config, date_created, date_updated)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

            course_basics["id"] = self.execute(sql, (course_basics["title"], course_basics["visible"], course_details["introduction"], course_details["passcode"], course_details["email_address"], course_details["highlighted"], course_details["allow_students_download_submissions"], course_details["virtual_assistant_config"], course_details["date_created"], course_details["date_updated"], ))
            course_basics["exists"] = True

            self.update_when_content_updated("user")

        return course_basics["id"]

    def save_assignment(self, assignment_basics, assignment_details):
        #TODO: Put this all in one transaction and add assignment group if it's not null.
        if assignment_basics["exists"]:
            sql = '''UPDATE assignments
                     SET title = ?, visible = ?, introduction = ?, date_updated = ?, start_date = ?, due_date = ?, allow_late = ?, late_percent = ?, view_answer_late = ?, has_timer = ?, hour_timer = ?, minute_timer = ?, restrict_other_assignments = ?, allowed_ip_addresses = ?, allowed_external_urls = ?, show_run_button = ?, custom_scoring = ?, require_security_codes = ?, support_questions = ?,  use_virtual_assistant = ?,
                     assignment_group_id = ?
                     WHERE course_id = ?
                       AND assignment_id = ?'''

            self.execute(sql, [assignment_basics["title"], assignment_basics["visible"], assignment_details["introduction"], assignment_details["date_updated"], assignment_details["start_date"], assignment_details["due_date"], assignment_details["allow_late"], assignment_details["late_percent"], assignment_details["view_answer_late"], assignment_details["has_timer"], assignment_details["hour_timer"], assignment_details["minute_timer"], assignment_details["restrict_other_assignments"], assignment_details["allowed_ip_addresses"], assignment_details["allowed_external_urls"], assignment_details["show_run_button"], assignment_details["custom_scoring"], assignment_details["require_security_codes"], assignment_details["support_questions"],   assignment_details["use_virtual_assistant"], assignment_details["assignment_group_id"], assignment_basics["course"]["id"], assignment_basics["id"]])
        else:
            sql = '''INSERT INTO assignments (course_id, title, visible, introduction, date_created, date_updated, start_date, due_date, allow_late, late_percent, view_answer_late, has_timer, hour_timer, minute_timer, restrict_other_assignments, allowed_ip_addresses, allowed_external_urls, show_run_button, custom_scoring, require_security_codes, support_questions,  use_virtual_assistant, assignment_group_id)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

            assignment_basics["id"] = self.execute(sql, [assignment_basics["course"]["id"], assignment_basics["title"], assignment_basics["visible"], assignment_details["introduction"], assignment_details["date_created"], assignment_details["date_updated"], assignment_details["start_date"], assignment_details["due_date"], assignment_details["allow_late"], assignment_details["late_percent"], assignment_details["view_answer_late"], assignment_details["has_timer"], assignment_details["hour_timer"], assignment_details["minute_timer"], assignment_details["restrict_other_assignments"], assignment_details["allowed_ip_addresses"], assignment_details["allowed_external_urls"], assignment_details["show_run_button"], assignment_details["custom_scoring"], assignment_details["require_security_codes"], assignment_details["support_questions"],  assignment_details["use_virtual_assistant"], assignment_details["assignment_group_id"]])
            assignment_basics["exists"] = True

        sql_statements = ['''DELETE FROM prerequisite_assignments
                             WHERE course_id = ? AND assignment_id = ?''']
        param_lists = [(assignment_basics["course"]["id"], assignment_basics["id"], )]

        for prerequisite_assignment_id in assignment_details["prerequisite_assignment_ids"]:
            sql_statements.append('''INSERT INTO prerequisite_assignments (course_id, assignment_id, prerequisite_assignment_id)
                                     VALUES (?, ?, ?)''')
            param_lists.append((assignment_basics["course"]["id"], assignment_basics["id"], prerequisite_assignment_id))

        self.execute_multiple(sql_statements, param_lists)

        sql_statements = ['''DELETE FROM assignment_early_exceptions
                             WHERE course_id = ? AND assignment_id = ?''']
        param_lists = [(assignment_basics["course"]["id"], assignment_basics["id"], )]

        for user_id in assignment_details["student_early_exceptions"]:
            sql_statements.append('''INSERT INTO assignment_early_exceptions (course_id, assignment_id, user_id)
                                     VALUES (?, ?, ?)''')
            param_lists.append((assignment_basics["course"]["id"], assignment_basics["id"], user_id))

        sql_statements.append('''DELETE FROM assignment_late_exceptions
                             WHERE course_id = ? AND assignment_id = ?''')
        param_lists.append((assignment_basics["course"]["id"], assignment_basics["id"], ))

        for user_id in assignment_details["student_late_exceptions"]:
            sql_statements.append('''INSERT INTO assignment_late_exceptions (course_id, assignment_id, user_id)
                                     VALUES (?, ?, ?)''')
            param_lists.append((assignment_basics["course"]["id"], assignment_basics["id"], user_id))

        sql_statements.append('''DELETE FROM assignment_timer_exceptions
                             WHERE course_id = ? AND assignment_id = ?''')
        param_lists.append((assignment_basics["course"]["id"], assignment_basics["id"], ))

        for user_id, timer_info in assignment_details["student_timer_exceptions"].items():
            sql_statements.append('''INSERT INTO assignment_timer_exceptions (course_id, assignment_id, user_id, hour_timer, minute_timer)
                                     VALUES (?, ?, ?, ?, ?)''')
            param_lists.append((assignment_basics["course"]["id"], assignment_basics["id"], user_id, timer_info[0], timer_info[1]))

        self.execute_multiple(sql_statements, param_lists)

        self.update_when_content_updated(assignment_basics["course"]["id"])

        return assignment_basics["id"]

    def save_exercise(self, exercise_basics, exercise_details):
        cursor = self.conn.cursor()
        cursor.execute("BEGIN")

        if "what_students_see_after_success" not in exercise_details:
            exercise_details["what_students_see_after_success"] = 1

        try:
            if exercise_basics["exists"]:
                sql = '''
                    UPDATE exercises
                    SET title = ?, visible = ?, solution_code = ?, solution_description = ?, hint = ?,
                        max_submissions = ?, credit = ?, data_files = ?, back_end = ?,
                        instructions = ?, output_type = ?, allow_any_response = ?,
                        what_students_see_after_success = ?, starter_code = ?,
                        date_updated = ?, enable_pair_programming = ?, verification_code = ?,
                        weight = ?,
                        min_solution_length = ?,
                        max_solution_length = ?
                    WHERE course_id = ?
                      AND assignment_id = ?
                      AND exercise_id = ?'''

                cursor.execute(sql, [exercise_basics["title"], exercise_basics["visible"], str(exercise_details["solution_code"]), exercise_details["solution_description"], exercise_details["hint"], exercise_details["max_submissions"], exercise_details["credit"], json.dumps(exercise_details["data_files"], default=str), exercise_details["back_end"], exercise_details["instructions"], exercise_details["output_type"], exercise_details["allow_any_response"], exercise_details["what_students_see_after_success"], exercise_details["starter_code"], exercise_details["date_updated"], exercise_details["enable_pair_programming"], exercise_details["verification_code"], exercise_details["weight"], exercise_details["min_solution_length"], exercise_details["max_solution_length"],  exercise_basics["assignment"]["course"]["id"], exercise_basics["assignment"]["id"], exercise_basics["id"]])

                sql = '''DELETE FROM test_outputs
                         WHERE test_id IN (
                           SELECT test_id
                           FROM tests
                           WHERE course_id = ?
                             AND assignment_id = ?
                             AND exercise_id = ?)'''

                cursor.execute(sql, [exercise_basics["assignment"]["course"]["id"], exercise_basics["assignment"]["id"], exercise_basics["id"]])

                sql = '''DELETE FROM tests
                         WHERE course_id = ?
                           AND assignment_id = ?
                           AND exercise_id = ?'''

                cursor.execute(sql, [exercise_basics["assignment"]["course"]["id"], exercise_basics["assignment"]["id"], exercise_basics["id"]])

                for title in exercise_details["tests"]:
                    # Only saves 'jpg_output' if it isn't blank.
                    jpg_output = exercise_details["tests"][title]["jpg_output"]
                    #if jpg_output != "" and jpg_output.strip() == BLANK_IMAGE.strip():
                    if jpg_output != "" and jpg_output.strip() == BLANK_IMAGE:
                        jpg_output = ""

                    sql = '''INSERT INTO tests (course_id, assignment_id, exercise_id, title, before_code, after_code, instructions, can_see_test_code, can_see_expected_output, can_see_code_output, txt_output, jpg_output)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

                    test_id = cursor.execute(sql, [exercise_basics["assignment"]["course"]["id"], exercise_basics["assignment"]["id"], exercise_basics["id"], title, exercise_details["tests"][title]["before_code"], exercise_details["tests"][title]["after_code"], exercise_details["tests"][title]["instructions"], exercise_details["tests"][title]["can_see_test_code"], exercise_details["tests"][title]["can_see_expected_output"], exercise_details["tests"][title]["can_see_code_output"], exercise_details["tests"][title]["txt_output"], jpg_output])
            else:
                sql = '''INSERT INTO exercises (course_id, assignment_id, title, visible, solution_code, solution_description, hint, max_submissions, credit, data_files, back_end, instructions, output_type, allow_any_response, what_students_see_after_success, starter_code, date_created, date_updated, enable_pair_programming, verification_code, weight, min_solution_length, max_solution_length)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

                cursor.execute(sql, [exercise_basics["assignment"]["course"]["id"], exercise_basics["assignment"]["id"], exercise_basics["title"], exercise_basics["visible"], str(exercise_details["solution_code"]), exercise_details["solution_description"], exercise_details["hint"], exercise_details["max_submissions"], exercise_details["credit"], json.dumps(exercise_details["data_files"], default=str), exercise_details["back_end"], exercise_details["instructions"], exercise_details["output_type"], exercise_details["allow_any_response"], exercise_details["what_students_see_after_success"], exercise_details["starter_code"], exercise_details["date_created"], exercise_details["date_updated"], exercise_details["enable_pair_programming"], exercise_details["verification_code"], exercise_details["weight"], exercise_details["min_solution_length"], exercise_details["max_solution_length"]])

                exercise_basics["id"] = cursor.lastrowid
                exercise_basics["exists"] = True

                for title in exercise_details["tests"]:
                    sql = '''INSERT INTO tests (course_id, assignment_id, exercise_id, title, before_code, after_code, instructions, txt_output, jpg_output, can_see_test_code, can_see_expected_output, can_see_code_output)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

                    test_id = cursor.execute(sql, [
                        exercise_basics["assignment"]["course"]["id"],
                        exercise_basics["assignment"]["id"],
                        exercise_basics["id"],
                        title,
                        exercise_details["tests"][title]["before_code"],
                        exercise_details["tests"][title]["after_code"],
                        exercise_details["tests"][title]["instructions"],
                        exercise_details["tests"][title]["txt_output"],
                        exercise_details["tests"][title]["jpg_output"],
                        exercise_details["tests"][title]["can_see_test_code"],
                        exercise_details["tests"][title]["can_see_expected_output"],
                        exercise_details["tests"][title]["can_see_code_output"],
                    ])

            cursor.execute("COMMIT")
        except self.conn.Error:
            cursor.execute("ROLLBACK")
            raise

        cursor.close()

        self.update_when_content_updated(exercise_basics["assignment"]["course"]["id"])

        return exercise_basics["id"]

    def save_presubmission(self, course_id, assignment_id, exercise_id, user_id, presubmission):
        sql = '''INSERT OR REPLACE INTO presubmissions (course_id, assignment_id, exercise_id, user_id, presubmission)
                 VALUES (?, ?, ?, ?, ?)'''

        self.execute(sql, [course_id, assignment_id, exercise_id, user_id, presubmission])

    async def save_thumb_status(self, course_id, assignment_id, exercise_id, user_id, item_description, status):
        sql = '''INSERT OR REPLACE INTO thumbs (course_id, assignment_id, exercise_id, user_id, item_description, status)
                 VALUES (?, ?, ?, ?, ?, ?)'''

        self.execute(sql, [course_id, assignment_id, exercise_id, user_id, item_description, status])

    async def get_thumb_status(self, course_id, assignment_id, exercise_id, user_id, item_description):
        sql = '''SELECT status
                 FROM thumbs
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND exercise_id = ?
                   AND user_id = ?
                   AND item_description = ?'''

        result = self.fetchone(sql, (course_id, assignment_id, exercise_id, user_id, item_description))

        status = -1
        if result:
            status = result["status"]

        return status

    async def save_submission(self, course_id, assignment_id, exercise_id, user_id, code, passed, date, exercise_details, test_outputs, score, partner_id):
        insert_submission = True

        if exercise_details["back_end"] == "multiple_choice":
            submissions = self.get_submissions(course_id, assignment_id, exercise_id, user_id, exercise_details)

            if len(submissions[1]) > 0:
                submission_id = submissions[1][0]["id"]
                sql = '''UPDATE submissions
                         SET code = ?,
                             passed = ?,
                             date = ?,
                             partner_id = ?
                         WHERE submission_id = ?'''
                
                self.execute(sql, (code, passed, date, partner_id, submission_id))
                
                insert_submission = False

        if insert_submission:
            sql = '''INSERT INTO submissions (course_id, assignment_id, exercise_id, user_id, code, passed, date, partner_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''

            submission_id = self.execute(sql, (course_id, assignment_id, exercise_id, user_id, code, passed, date, partner_id))

        sql_statements = []
        params_list = []

        for test_title, test_dict in test_outputs.items():
            if test_dict["jpg_output"] != "":
                if test_dict["jpg_output"].strip() == BLANK_IMAGE:
                    test_dict["jpg_output"] = ""

            sql_statements.append('''INSERT INTO test_outputs (test_id, submission_id, txt_output, jpg_output)
                      VALUES (?, ?, ?, ?)''')

            params_list.append((exercise_details["tests"][test_title]["test_id"], submission_id, test_dict["txt_output"], test_dict["jpg_output"],))

        self.execute_multiple(sql_statements, params_list)

        self.save_exercise_score(course_id, assignment_id, exercise_id, user_id, score)

        # if exercise_details["back_end"] != "multiple_choice":
        self.save_presubmission(course_id, assignment_id, exercise_id, user_id, code)

        return submission_id
    
        # sql = '''INSERT INTO submissions (course_id, assignment_id, exercise_id, user_id, code, passed, date, partner_id)
        #          VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''

        # submission_id = self.execute(sql, [int(course_id), int(assignment_id), int(exercise_id), user_id, code, passed, date, partner_id])

        # #TODO: Execute this all in one transaction
        # #      https://stackoverflow.com/questions/54289555/how-do-i-execute-an-sqlite-script-from-within-python
        # if len(test_outputs) > 0:
        #     test_sql = '''INSERT INTO test_outputs (test_id, submission_id, txt_output, jpg_output)
        #                   VALUES (?, ?, ?, ?)'''

        #     for test_title, test_dict in test_outputs.items():
        #         if test_dict["jpg_output"] != "":
        #             #if test_dict["jpg_output"].strip() == BLANK_IMAGE.strip():
        #             if test_dict["jpg_output"].strip() == BLANK_IMAGE:
        #                 test_dict["jpg_output"] = ""

        #         self.execute(test_sql, [exercise_details["tests"][test_title]["test_id"], submission_id, test_dict["txt_output"], test_dict["jpg_output"]])

        # self.save_presubmission(course_id, assignment_id, exercise_id, user_id, code)

        # return submission_id

    async def copy_course(self, existing_course_basics, new_course_title):
        # Copy the high-level course info and get a new course ID.
        sql = '''INSERT INTO courses (title, introduction, visible, passcode, email_address, highlighted, allow_students_download_submissions, virtual_assistant_config, date_created, date_updated)
                 SELECT ?, introduction, visible, passcode, email_address, highlighted, allow_students_download_submissions, virtual_assistant_config, date_created, date_updated
                 FROM courses
                 WHERE course_id = ?'''

        new_course_id = self.execute(sql, (new_course_title, existing_course_basics['id']))

        # Copy each assignment group.
        sql = '''INSERT INTO assignment_groups(course_id, title)
                 SELECT ?, title
                 FROM assignment_groups
                 WHERE course_id = ?'''
        self.execute(sql, (new_course_id, existing_course_basics['id']))

        assignment_id_mapping = {}

        # Copy each assignment and get new assignment IDs.
        for assignment_basics in self.get_assignments(existing_course_basics):
            sql = '''INSERT INTO assignments (course_id, title, visible, introduction, date_created, date_updated, start_date, due_date, allow_late, late_percent, view_answer_late, has_timer, hour_timer, minute_timer, restrict_other_assignments, allowed_ip_addresses, allowed_external_urls, show_run_button, custom_scoring, require_security_codes, support_questions,  use_virtual_assistant, assignment_group_id)
                     SELECT ?, a.title, a.visible, a.introduction, a.date_created, a.date_updated, a.start_date, a.due_date, a.allow_late, a.late_percent, a.view_answer_late, a.has_timer, a.hour_timer, a.minute_timer, a.restrict_other_assignments, a.allowed_ip_addresses, a.allowed_external_urls, a.show_run_button, a.custom_scoring, a.require_security_codes, a.support_questions, a.use_virtual_assistant, (SELECT ag2.assignment_group_id FROM assignment_groups ag2 WHERE ag2.course_id = ? AND ag2.title = ag.title)
                     FROM assignments a
                     LEFT JOIN assignment_groups ag
                       ON a.course_id = ag.course_id AND a.assignment_group_id = ag.assignment_group_id
                     WHERE a.course_id = ?
                       AND a.assignment_id = ?'''

            new_assignment_id = self.execute(sql, (new_course_id, new_course_id, existing_course_basics['id'], assignment_basics[0]))

            assignment_id_mapping[assignment_basics[0]] = new_assignment_id

            # Copy each exercise from each assignment.
            sql = '''SELECT exercise_id
                     FROM exercises
                     WHERE course_id = ?
                       AND assignment_id = ?'''

            old_exercise_ids = [row["exercise_id"] for row in self.fetchall(sql, (existing_course_basics['id'], assignment_basics[0],))]

            for exercise_id in old_exercise_ids:
                sql = '''INSERT INTO exercises (course_id, assignment_id, title, visible, solution_code, solution_description, hint, max_submissions, credit, data_files, back_end, instructions, output_type, what_students_see_after_success, starter_code, date_created, date_updated, enable_pair_programming, verification_code, weight, min_solution_length, max_solution_length, allow_any_response)
                         SELECT ?, ?, title, visible, solution_code, solution_description, hint, max_submissions, credit, data_files, back_end, instructions, output_type, what_students_see_after_success, starter_code, date_created, date_updated, enable_pair_programming, verification_code, weight, min_solution_length, max_solution_length,  allow_any_response
                         FROM exercises
                         WHERE course_id = ?
                           AND assignment_id = ?
                           AND exercise_id = ?'''

                new_exercise_id = self.execute(sql, (new_course_id, new_assignment_id, existing_course_basics['id'], assignment_basics[0], exercise_id))

                # Copy tests associated with each exercise
                sql = '''INSERT INTO tests (course_id, assignment_id, exercise_id, title, before_code, after_code, instructions, txt_output, jpg_output, can_see_test_code, can_see_expected_output, can_see_code_output)
                         SELECT ?, ?, ?, title, before_code, after_code, instructions, txt_output, jpg_output, can_see_test_code, can_see_expected_output, can_see_code_output
                         FROM tests
                         WHERE course_id = ?
                           AND assignment_id = ?
                           AND exercise_id = ?'''

                self.execute(sql, (new_course_id, new_assignment_id, new_exercise_id, existing_course_basics['id'], assignment_basics[0], exercise_id))

                # Copy questions associated with each exercise
                sql = '''INSERT INTO questions (course_id, assignment_id, exercise_id, questioner_id, question, questioner_share, question_modified, answerer_id, answer, answerer_share)
                         SELECT ?, ?, ?, questioner_id, question, questioner_share, question_modified, answerer_id, answer, answerer_share
                         FROM questions
                         WHERE course_id = ?
                           AND assignment_id = ?
                           AND exercise_id = ?
                           AND questioner_share = 1
                           AND answer IS NOT NULL
                           AND answerer_share = 1'''

                self.execute(sql, (new_course_id, new_assignment_id, new_exercise_id, existing_course_basics['id'], assignment_basics[0], exercise_id))

        # Copy prerequisite assignments.
        for old_assignment_id, new_assignment_id in assignment_id_mapping.items():
            # First, get old prerequisite assignment IDs.
            sql = '''SELECT prerequisite_assignment_id as id
                     FROM prerequisite_assignments
                     WHERE course_id = ?
                       AND assignment_id = ?'''

            old_prerequisite_ids = [row["id"] for row in self.fetchall(sql, (existing_course_basics['id'], old_assignment_id,))]

            # Second, insert the one IDs.
            for old in old_prerequisite_ids:
                new_prerequisite_id = assignment_id_mapping[old]

                sql = '''INSERT INTO prerequisite_assignments (course_id, assignment_id, prerequisite_assignment_id)
                         VALUES (?, ?, ?)'''

                self.execute(sql, (new_course_id, new_assignment_id, new_prerequisite_id,))

        # Copy permissions for instructors and assistants.
        sql = '''INSERT INTO permissions (user_id, role, course_id)
                 SELECT user_id, role, ?
                 FROM permissions
                 WHERE course_id = ?'''

        self.execute(sql, (new_course_id, existing_course_basics['id'],))

        self.update_when_content_updated(new_course_id)

    def copy_assignment(self, course_id, assignment_id, new_title):
        sql = '''INSERT INTO assignments (course_id, title, visible, introduction, date_created, date_updated, start_date, due_date, allow_late, late_percent, view_answer_late, has_timer, hour_timer, minute_timer, restrict_other_assignments, allowed_ip_addresses, allowed_external_urls, show_run_button, custom_scoring,  require_security_codes, support_questions, use_virtual_assistant, assignment_group_id)
                 SELECT course_id, ?, visible, introduction, date_created, date_updated, start_date, due_date, allow_late, late_percent, view_answer_late, has_timer, hour_timer, minute_timer, restrict_other_assignments, allowed_ip_addresses, allowed_external_urls, show_run_button, custom_scoring,  require_security_codes, support_questions, use_virtual_assistant, assignment_group_id
                 FROM assignments
                 WHERE course_id = ?
                   AND assignment_id = ?'''

        new_assignment_id = self.execute(sql, (new_title, course_id, assignment_id,))

        sql = '''SELECT exercise_id
                 FROM exercises
                 WHERE course_id = ?
                   AND assignment_id = ?'''

        old_exercise_ids = [row["exercise_id"] for row in self.fetchall(sql, (course_id, assignment_id,))]

        for exercise_id in old_exercise_ids:
            sql = '''INSERT INTO exercises (course_id, assignment_id, title, visible, solution_code, solution_description, hint, max_submissions, credit, data_files, back_end, instructions, output_type, what_students_see_after_success, starter_code, date_created, date_updated, enable_pair_programming, verification_code, weight, min_solution_length, max_solution_length, allow_any_response)
                     SELECT course_id, ?, title, visible, solution_code, solution_description, hint, max_submissions, credit, data_files, back_end, instructions, output_type, what_students_see_after_success, starter_code, date_created, date_updated, enable_pair_programming, verification_code, weight, min_solution_length, max_solution_length, allow_any_response
                     FROM exercises
                     WHERE course_id = ?
                       AND assignment_id = ?
                       AND exercise_id = ?'''

            new_exercise_id = self.execute(sql, (new_assignment_id, course_id, assignment_id, exercise_id))

            sql = '''INSERT INTO tests (course_id, assignment_id, exercise_id, title, before_code, after_code, instructions, txt_output, jpg_output, can_see_test_code, can_see_expected_output, can_see_code_output)
                     SELECT course_id, ?, ?, title, before_code, after_code, instructions, txt_output, jpg_output, can_see_test_code, can_see_expected_output, can_see_code_output
                     FROM tests
                     WHERE course_id = ?
                       AND assignment_id = ?
                       AND exercise_id = ?'''

            self.execute(sql, (new_assignment_id, new_exercise_id, course_id, assignment_id, exercise_id))

        self.update_when_content_updated(course_id)

    def copy_exercise(self, course_id, assignment_id, exercise_id, new_title):
        try:
            sql = '''INSERT INTO exercises (course_id, assignment_id, title, visible, solution_code, solution_description, hint, max_submissions, credit, data_files, back_end, instructions, output_type, what_students_see_after_success, starter_code, date_created, date_updated, enable_pair_programming, verification_code, weight, min_solution_length, max_solution_length, allow_any_response)
                     SELECT course_id, assignment_id, ?, visible, solution_code, solution_description, hint, max_submissions, credit, data_files, back_end, instructions, output_type, what_students_see_after_success, starter_code, date_created, date_updated, enable_pair_programming, verification_code, weight, min_solution_length, max_solution_length, allow_any_response
                     FROM exercises
                     WHERE course_id = ?
                         AND assignment_id = ?
                         AND exercise_id = ?'''

            new_exercise_id = self.execute(sql, (new_title, course_id, assignment_id, exercise_id, ))

            sql = '''INSERT INTO tests (course_id, assignment_id, exercise_id, title, before_code, after_code, instructions, txt_output, jpg_output, can_see_test_code, can_see_expected_output, can_see_code_output)
                     SELECT course_id, assignment_id, ?, title, before_code, after_code, instructions, txt_output, jpg_output, can_see_test_code, can_see_expected_output, can_see_code_output
                     FROM tests
                     WHERE course_id = ?
                       AND assignment_id = ?
                       AND exercise_id = ?'''

            self.execute(sql, (new_exercise_id, course_id, assignment_id, exercise_id, ))
        except:
            print(traceback.format_exc())

        self.update_when_content_updated(course_id)

    def update_user(self, user_id, user_dict):
        self.set_user_dict_defaults(user_dict)

        sql = '''UPDATE users
                 SET name = ?, given_name = ?, family_name = ?, locale = ?, email_address = ?
                 WHERE user_id = ?'''

        self.execute(sql, (user_dict["name"], user_dict["given_name"], user_dict["family_name"], user_dict["locale"], user_dict["email_address"], user_id,))

        self.update_when_content_updated("user")

    def update_user_settings(self, user_id, preferences_dict):
        sql = '''UPDATE users
                 SET ace_theme = ?, use_auto_complete = ?, use_studio_mode = ?, enable_vim = ?
                 WHERE user_id = ?'''

        self.execute(sql, (preferences_dict["ace_theme"], preferences_dict["use_auto_complete"], preferences_dict["use_studio_mode"], preferences_dict["enable_vim"], user_id))

        self.update_when_content_updated("user")

    def delete_user(self, user_id):
        sql = '''SELECT course_id
                 FROM course_registrations
                 WHERE user_id = ?'''
        
        for row in self.fetchall(sql, (user_id,)):
            self.update_when_content_updated(row["course_id"])

        sql_statements = []
        params_list = []
        for table_name in ["course_registrations", "presubmissions", "user_assignment_starts", "assignment_early_exceptions", "assignment_late_exceptions", "assignment_timer_exceptions", "scores", "submissions", "permissions", "users"]:
            sql_statements.append(f"DELETE FROM {table_name} WHERE user_id = ?")
            params_list.append((user_id, ))
        
        self.execute_multiple(sql_statements, params_list)

        self.update_when_content_updated("user")

    def move_assignment(self, course_id, assignment_id, new_course_id):
        for table in ["assignments", "exercises", "tests"]:
            self.execute(f'''UPDATE {table}
                             SET course_id = ?
                             WHERE course_id = ?
                               AND assignment_id = ?''', (new_course_id, course_id, assignment_id))

        for table in ["presubmissions", "scores", "submissions", "user_assignment_starts", "prerequisite_assignments", "assignment_early_exceptions",  "assignment_late_exceptions", "assignment_timer_exceptions", "virtual_assistant_interactions", "questions", "thumbs"]:
            self.execute(f'''DELETE FROM {table}
                             WHERE course_id = ?
                               AND assignment_id = ?''', (course_id, assignment_id))
            
        self.update_when_content_updated(course_id)

    #TODO: Make this like move_assignment
    def move_exercise(self, course_id, assignment_id, exercise_id, new_assignment_id):
        self.execute('''UPDATE exercises
                        SET assignment_id = ?
                        WHERE course_id = ?
                          AND assignment_id = ?
                          AND exercise_id = ?''', (new_assignment_id, course_id, assignment_id, exercise_id, ))

        self.execute('''UPDATE scores
                        SET assignment_id = ?
                        WHERE course_id = ?
                          AND assignment_id = ?
                          AND exercise_id = ?''', (new_assignment_id, course_id, assignment_id, exercise_id, ))

        self.execute('''UPDATE submissions
                        SET assignment_id = ?
                        WHERE course_id = ?
                          AND assignment_id = ?
                          AND exercise_id = ?''', (new_assignment_id, course_id, assignment_id, exercise_id, ))

        self.execute('''UPDATE presubmissions
                        SET assignment_id = ?
                        WHERE course_id = ?
                          AND assignment_id = ?
                          AND exercise_id = ?''', (new_assignment_id, course_id, assignment_id, exercise_id, ))

        self.execute('''UPDATE scores
                        SET assignment_id = ?
                        WHERE course_id = ?
                          AND assignment_id = ?
                          AND exercise_id = ?''', (new_assignment_id, course_id, assignment_id, exercise_id, ))

        self.execute('''UPDATE tests
                        SET assignment_id = ?
                        WHERE course_id = ?
                          AND assignment_id = ?
                          AND exercise_id = ?''', (new_assignment_id, course_id, assignment_id, exercise_id, ))
        
        self.execute('''UPDATE virtual_assistant_interactions
                        SET assignment_id = ?
                        WHERE course_id = ?
                          AND assignment_id = ?
                          AND exercise_id = ?''', (new_assignment_id, course_id, assignment_id, exercise_id, ))
        
        self.execute('''UPDATE questions
                        SET assignment_id = ?
                        WHERE course_id = ?
                          AND assignment_id = ?
                          AND exercise_id = ?''', (new_assignment_id, course_id, assignment_id, exercise_id, ))
        
        self.execute('''UPDATE thumbs
                        SET assignment_id = ?
                        WHERE course_id = ?
                          AND assignment_id = ?
                          AND exercise_id = ?''', (new_assignment_id, course_id, assignment_id, exercise_id, ))
        
        self.update_when_content_updated(course_id)

    #TODO: Clean up all of these delete functions.
    def delete_exercise(self, course_id, assignment_id, exercise_id):
        self.execute('''DELETE FROM submissions
                        WHERE course_id = ?
                          AND assignment_id = ?
                          AND exercise_id = ?''', (course_id, assignment_id, exercise_id, ))

        self.execute('''DELETE FROM presubmissions
                        WHERE course_id = ?
                          AND assignment_id = ?
                          AND exercise_id = ?''', (course_id, assignment_id, exercise_id, ))

        self.execute('''DELETE FROM scores
                        WHERE course_id = ?
                          AND assignment_id = ?
                          AND exercise_id = ?''', (course_id, assignment_id, exercise_id, ))

        self.execute('''DELETE FROM exercises
                        WHERE course_id = ?
                          AND assignment_id = ?
                          AND exercise_id = ?''', (course_id, assignment_id, exercise_id, ))

        self.execute('''DELETE FROM tests
                        WHERE course_id = ?
                          AND assignment_id = ?
                          AND exercise_id = ?''', (course_id, assignment_id, exercise_id, ))

        self.execute('''DELETE FROM test_outputs
                        WHERE submission_id IN (
                          SELECT submission_id
                          FROM submissions
                          WHERE course_id = ?
                          AND assignment_id = ?
                          AND exercise_id = ?)''', (course_id, assignment_id, exercise_id, ))

        self.execute('''DELETE FROM virtual_assistant_interactions
                        WHERE course_id = ?
                          AND assignment_id = ?
                          AND exercise_id = ?''', (course_id, assignment_id, exercise_id, ))
        
        self.execute('''DELETE FROM questions
                        WHERE course_id = ?
                          AND assignment_id = ?
                          AND exercise_id = ?''', (course_id, assignment_id, exercise_id, ))
        
        self.execute('''DELETE FROM thumbs
                        WHERE course_id = ?
                          AND assignment_id = ?
                          AND exercise_id = ?''', (course_id, assignment_id, exercise_id, ))
        
        self.update_when_content_updated(course_id)

    def delete_assignment(self, assignment_basics):
        course_id = assignment_basics["course"]["id"]
        assignment_id = assignment_basics["id"]

        self.execute('''DELETE FROM tests
                        WHERE course_id = ?
                          AND assignment_id = ?''', (course_id, assignment_id, ))

        self.execute('''DELETE FROM test_outputs
                        WHERE submission_id IN (
                          SELECT submission_id
                          FROM submissions
                          WHERE course_id = ?
                          AND assignment_id = ?)''', (course_id, assignment_id, ))

        self.execute('''DELETE FROM presubmissions
                        WHERE course_id = ?
                          AND assignment_id = ?''', (course_id, assignment_id, ))

        self.execute('''DELETE FROM submissions
                        WHERE course_id = ?
                          AND assignment_id = ?''', (course_id, assignment_id, ))

        self.execute('''DELETE FROM scores
                        WHERE course_id = ?
                          AND assignment_id = ?''', (course_id, assignment_id, ))

        self.execute('''DELETE FROM user_assignment_starts
                        WHERE course_id = ?
                          AND assignment_id = ?''', (course_id, assignment_id, ))
        
        self.execute('''DELETE FROM prerequisite_assignments
                        WHERE course_id = ?
                          AND (assignment_id = ? OR prerequisite_assignment_id = ?)
                          ''', (course_id, assignment_id, assignment_id))

        self.execute('''DELETE FROM assignment_early_exceptions
                        WHERE course_id = ?
                          AND assignment_id = ?''', (course_id, assignment_id, ))

        self.execute('''DELETE FROM assignment_late_exceptions
                        WHERE course_id = ?
                          AND assignment_id = ?''', (course_id, assignment_id, ))

        self.execute('''DELETE FROM assignment_timer_exceptions
                        WHERE course_id = ?
                          AND assignment_id = ?''', (course_id, assignment_id, ))
        
        self.execute('''DELETE FROM security_codes
                        WHERE course_id = ?
                          AND assignment_id = ?''', (course_id, assignment_id, ))
        
        self.execute('''DELETE FROM virtual_assistant_interactions
                        WHERE course_id = ?
                          AND assignment_id = ?''', (course_id, assignment_id, ))

        self.execute('''DELETE FROM questions
                        WHERE course_id = ?
                          AND assignment_id = ?''', (course_id, assignment_id, ))
        
        self.execute('''DELETE FROM thumbs
                        WHERE course_id = ?
                          AND assignment_id = ?''', (course_id, assignment_id, ))

        self.execute('''DELETE FROM exercises
                        WHERE course_id = ?
                          AND assignment_id = ?''', (course_id, assignment_id, ))

        self.execute('''DELETE FROM assignments
                        WHERE course_id = ?
                          AND assignment_id = ?''', (course_id, assignment_id, ))
        
        self.update_when_content_updated(course_id)

    def delete_course(self, course_id):
        self.execute('''DELETE FROM presubmissions
                        WHERE course_id = ?''', (course_id, ))

        self.execute('''DELETE FROM tests
                        WHERE course_id = ?''', (course_id, ))

        self.execute('''DELETE FROM test_outputs
                        WHERE submission_id IN (
                          SELECT submission_id
                          FROM submissions
                          WHERE course_id = ?)''', (course_id, ))

        self.execute('''DELETE FROM submissions
                        WHERE course_id = ?''', (course_id, ))

        self.execute('''DELETE FROM exercises
                        WHERE course_id = ?''', (course_id, ))

        self.execute('''DELETE FROM assignments
                        WHERE course_id = ?''', (course_id, ))

        self.execute('''DELETE FROM assignment_groups
                        WHERE course_id = ?''', (course_id, ))

        self.execute('''DELETE FROM courses
                        WHERE course_id = ?''', (course_id, ))

        self.execute('''DELETE FROM scores
                        WHERE course_id = ?''', (course_id, ))

        self.execute('''DELETE FROM course_registrations
                        WHERE course_id = ?''', (course_id, ))

        self.execute('''DELETE FROM permissions
                        WHERE course_id = ?''', (course_id, ))

        self.execute('''DELETE FROM user_assignment_starts
                        WHERE course_id = ?''', (course_id, ))
        
        self.execute('''DELETE FROM prerequisite_assignments
                        WHERE course_id = ?''', (course_id, ))

        self.execute('''DELETE FROM assignment_early_exceptions
                        WHERE course_id = ?''', (course_id, ))

        self.execute('''DELETE FROM assignment_late_exceptions
                        WHERE course_id = ?''', (course_id, ))

        self.execute('''DELETE FROM assignment_timer_exceptions
                        WHERE course_id = ?''', (course_id, ))
        
        self.execute('''DELETE FROM security_codes
                        WHERE course_id = ?''', (course_id, ))
        
        self.execute('''DELETE FROM virtual_assistant_interactions
                        WHERE course_id = ?''', (course_id, ))
        
        self.execute('''DELETE FROM questions
                        WHERE course_id = ?''', (course_id, ))
        
        self.execute('''DELETE FROM thumbs
                        WHERE course_id = ?''', (course_id, ))
        
        self.delete_content_updated(course_id)

    def delete_course_submissions(self, course_id):
        self.execute('''DELETE FROM submissions
                        WHERE course_id = ?''', (course_id, ))

        self.execute('''DELETE FROM scores
                        WHERE course_id = ?''', (course_id, ))

        self.execute('''DELETE FROM presubmissions
                        WHERE course_id = ?''', (course_id, ))

        self.execute('''DELETE FROM user_assignment_starts
                        WHERE course_id = ?''', (course_id, ))

        self.execute('''DELETE FROM test_outputs
                        WHERE submission_id IN (
                          SELECT submission_id
                          FROM submissions
                          WHERE course_id = ?)''', (course_id, ))
        
        self.execute('''DELETE FROM security_codes
                        WHERE course_id = ?''', (course_id, ))
        
        self.execute('''DELETE FROM virtual_assistant_interactions
                        WHERE course_id = ?''', (course_id, ))
        
        self.execute('''DELETE FROM thumbs
                        WHERE course_id = ?''', (course_id, ))

    def delete_assignment_submissions(self, assignment_basics):
        course_id = assignment_basics["course"]["id"]
        assignment_id = assignment_basics["id"]

        self.execute('''DELETE FROM submissions
                        WHERE course_id = ?
                          AND assignment_id = ?''', (course_id, assignment_id, ))

        self.execute('''DELETE FROM scores
                        WHERE course_id = ?
                          AND assignment_id = ?''', (course_id, assignment_id, ))

        self.execute('''DELETE FROM presubmissions
                        WHERE course_id = ?
                          AND assignment_id = ?''', (course_id, assignment_id, ))

        self.execute('''DELETE FROM user_assignment_starts
                        WHERE course_id = ?
                          AND assignment_id = ?''', (course_id, assignment_id, ))

        self.execute('''DELETE FROM test_outputs
                        WHERE submission_id IN (
                          SELECT submission_id
                          FROM submissions
                          WHERE course_id = ?
                          AND assignment_id = ?)''', (course_id, assignment_id, ))
        
        self.execute('''DELETE FROM security_codes
                        WHERE course_id = ?
                          AND assignment_id = ?''', (course_id, assignment_id, ))
        
        self.execute('''DELETE FROM virtual_assistant_interactions
                        WHERE course_id = ?
                          AND assignment_id = ?''', (course_id, assignment_id, ))
        
        self.execute('''DELETE FROM thumbs
                        WHERE course_id = ?
                          AND assignment_id = ?''', (course_id, assignment_id, ))

    async def delete_exercise_submissions(self, course_id, assignment_id, exercise_id):
        self.execute('''DELETE FROM submissions
                        WHERE course_id = ?
                          AND assignment_id = ?
                          AND exercise_id = ?''', (course_id, assignment_id, exercise_id, ))

        self.execute('''DELETE FROM scores
                        WHERE course_id = ?
                          AND assignment_id = ?
                          AND exercise_id = ?''', (course_id, assignment_id, exercise_id, ))

        self.execute('''DELETE FROM presubmissions
                        WHERE course_id = ?
                          AND assignment_id = ?
                          AND exercise_id = ?''', (course_id, assignment_id, exercise_id, ))
        
        self.execute('''DELETE FROM virtual_assistant_interactions
                        WHERE course_id = ?
                          AND assignment_id = ?
                          AND exercise_id = ?''', (course_id, assignment_id, exercise_id, ))
        
        self.execute('''DELETE FROM thumbs
                        WHERE course_id = ?
                          AND assignment_id = ?
                          AND exercise_id = ?''', (course_id, assignment_id, exercise_id, ))

        self.execute('''DELETE FROM test_outputs
                        WHERE submission_id IN (
                          SELECT submission_id
                          FROM submissions
                          WHERE course_id = ?
                          AND assignment_id = ?
                          AND exercise_id = ?)''', (course_id, assignment_id, exercise_id, ))

    async def create_assignment_scores_text(self, course_basics, assignment_basics, include_header=True):
        course_id = course_basics["title"]
        assignment_id = assignment_basics["title"]
        scores, total_times_pair_programmed = self.get_assignment_scores(course_basics, assignment_basics)

        if include_header:
            out_file_text = "Course\tAssignment\tStudent_ID\tNum_Completed\tScore\tLast_Submission\tNum_Times_Pair_Programmed\n"
        else:
            out_file_text = ""

        for student in scores:
            out_file_text += f"{course_id}\t{assignment_id}\t{student[0]}\t{student[1]['num_completed']}\t{student[1]['score']}\t{student[1]['last_submission_timestamp']}\t{student[1]['num_times_pair_programmed']}\n"

        return out_file_text

#    def export_data(self, course_basics, table_name, output_tsv_file_path):
#        if table_name == "submissions":
#            sql = '''SELECT c.title, a.title, e.title, s.user_id, s.submission_id, s.code, s.txt_output, s.jpg_output, s.passed, s.date
#                    FROM submissions s
#                    INNER JOIN courses c
#                      ON c.course_id = s.course_id
#                    INNER JOIN assignments a
#                      ON a.assignment_id = s.assignment_id
#                    INNER JOIN exercises e
#                      ON e.exercise_id = s.exercise_id
#                    WHERE s.course_id = ?'''
#
#        else:
#            sql = f"SELECT * FROM {table_name} WHERE course_id = ?"
#
#        rows = []
#        for row in self.fetchall(sql, (course_basics["id"],)):
#            row_values = []
#            for x in row:
#                if type(x) is datetime:
#                    x = str(x)
#                row_values.append(x)
#
#            rows.append(row_values)
#
#        with open(output_tsv_file_path, "w") as out_file:
#            out_file.write(json.dumps(rows, default=str))

#    def create_zip_file_path(self, descriptor):
#        temp_dir_path = "/database/tmp/{}".format(create_id())
#        zip_file_name = f"{descriptor}.zip"
#        zip_file_path = f"{temp_dir_path}/{zip_file_name}"
#        return temp_dir_path, zip_file_name, zip_file_path
#
#    def zip_export_files(self, temp_dir_path, zip_file_name, zip_file_path, descriptor):
#        os.system(f"cp ../VERSION {temp_dir_path}/{descriptor}/")
#        os.system(f"cd {temp_dir_path}; zip -r -qq {zip_file_path} .")
#
#    def create_export_paths(self, temp_dir_path, descriptor):
#        os.makedirs(temp_dir_path)
#        os.makedirs(f"{temp_dir_path}/{descriptor}")
#
#    def remove_export_paths(self, zip_file_path, tmp_dir_path):
#        if os.path.exists(zip_file_path):
#            os.remove(zip_file_path)
#
#        if os.path.exists(tmp_dir_path):
#            shutil.rmtree(tmp_dir_path, ignore_errors=True)

    # async def get_student_pairs(self, course_id, user_name):
    #     # Uses the week of the year as a seed.
    #     seed = get_current_datetime().isocalendar().week

    #     # Gets student names registered in a course (will add obscured emails to the end of the name in the case of duplicate names)
    #     students = list(self.get_partner_info(course_id, False).keys())

    #     # Randomizes students using seed
    #     random.Random(seed).shuffle(students)

    #     if len(students) == 0:
    #         pairs = []
    #     elif len(students) % 2 == 0:
    #         pairs = [[students[i], students[i + 1]] for i in range(0, len(students), 2)]
    #     else:
    #         # Create pairs for everyone except the last student.
    #         pairs = [[students[i], students[i + 1]] for i in range(0, len(students) - 1, 2)]

    #         # This code creates a trio.
    #         #pairs[-1].append(students[-1])

    #         # This code puts one person on their own.
    #         pairs.extend([[students[-1]]])

    #     # Indicates which pair the user is in.
    #     pairs = [{'is_user': True, 'pair': pair} if user_name in pair else {'is_user': False, 'pair': pair} for pair in pairs]

    #     return pairs

    def get_next_prev_student_ids(self, course_id, student_id):
        sql = '''SELECT u.user_id
                 FROM users u
                 INNER JOIN course_registrations cr
                   ON u.user_id = cr.user_id
                 WHERE cr.course_id = ?
                 ORDER BY u.name'''

        user_ids = [row["user_id"] for row in self.fetchall(sql, (course_id, ))]

        prev_student_id = None
        next_student_id = None

        if student_id in user_ids:
          student_index = user_ids.index(student_id)

          if student_index > 0:
              prev_student_id = user_ids[student_index - 1]
          if student_index < len(user_ids) - 1:
              next_student_id = user_ids[student_index + 1]

        return prev_student_id, next_student_id

    #TODO: sql = self.scores_statuses_temp_tables_sql??
    def get_submissions_student(self, course_id, student_id):
        sql = '''SELECT a.title AS assignment_title,
                        a.introduction AS assignment_introduction,
                        e.title AS exercise_title,
                        e.instructions AS exercise_instructions,
                        s.code,
                        max(s.date)
                 FROM submissions s
                 INNER JOIN exercises e
                   ON s.exercise_id = e.exercise_id
                 INNER JOIN assignments a
                   ON s.assignment_id = a.assignment_id
                 WHERE s.course_id = ?
                   AND s.user_id = ?
                   AND s.passed = 1
                   AND e.visible = 1
                   AND a.visible = 1
                   AND a.has_timer = 0
                   AND e.back_end != "not_code"
                 GROUP BY a.assignment_id, e.exercise_id'''

        submissions = []
        for row in self.fetchall(sql, (course_id, student_id,)):
            submission = {}
            for x in ["assignment_title", "assignment_introduction", "exercise_title", "exercise_instructions", "code"]:
                submission[x] = row[x]

            submissions.append(submission)

        return sort_list_of_dicts_nicely(submissions, ["assignment_title", "exercise_title"])
    
    def get_at_risk_students(self, course_id, num_hours_diff):
        sql = """
            SELECT DISTINCT cr.user_id, u.name, u.email_address, s.assignment_id, a.title AS assignment_title, s.exercise_id, e.title AS exercise_title, MAX(s.date) AS last_submission_date
            FROM course_registrations cr
            INNER JOIN submissions s
              ON cr.course_id = s.course_id
              AND cr.user_id = s.user_id
            INNER JOIN users u
              ON s.user_id = u.user_id
            INNER JOIN assignments a
              ON s.course_id = a.course_id
            AND s.assignment_id = a.assignment_id
            INNER JOIN exercises e
              ON s.course_id = e.course_id
            AND s.assignment_id = e.assignment_id
            AND s.exercise_id = e.exercise_id
            WHERE cr.course_id = ?
              AND u.user_id NOT IN (
                  SELECT user_id
                  FROM permissions
                  WHERE course_id = 0 OR course_id = ?
              )
            GROUP BY cr.user_id, u.name, u.email_address
            HAVING MAX(s.date) < datetime('now', '-' || ? || ' hours')
            
            UNION
            
            SELECT u.user_id, u.name, u.email_address, NULL, NULL, NULL, NULL, NULL
            FROM users u
            WHERE u.user_id IN (
              SELECT user_id
                FROM course_registrations
                WHERE course_id = ?
            )
              AND user_id NOT IN (
                  SELECT DISTINCT user_id
                  FROM submissions
                  WHERE course_id = ?

                  UNION

                  SELECT user_id
                  FROM permissions
                  WHERE course_id = 0 OR course_id = ?
              )
            ORDER BY cr.user_id
            """
        
        rows = []

        for row in self.fetchall(sql, (course_id, course_id, num_hours_diff, course_id, course_id, course_id, )):
            rows.append(dict(row))

        return rows
    
    def get_virtual_assistant_interactions(self, course_id, assignment_id, exercise_id, user_id):
        sql = """SELECT question, response
                 FROM virtual_assistant_interactions
                 WHERE course_id = ?
                   AND assignment_id = ?
                   AND exercise_id = ?
                   AND user_id = ?
                 ORDER BY when_interacted"""

        interactions = []

        for row in self.fetchall(sql, (course_id, assignment_id, exercise_id, user_id,)):
            interaction = {"question": row["question"], "response": row["response"]}

            interactions.append(interaction)

        return interactions

    def save_virtual_assistant_interaction(self, course_id, assignment_id, exercise_id, user_id, question, response):
        sql = """INSERT INTO virtual_assistant_interactions 
                 (course_id, assignment_id, exercise_id, user_id, question, response)
                 VALUES (?, ?, ?, ?, ?, ?)"""
        
        self.execute(sql, (course_id, assignment_id, exercise_id, user_id, question, response,))

    def save_question(self, course_id, assignment_id, exercise_id, questioner_id, question, questioner_share):
        sql = """INSERT INTO questions 
          (course_id, assignment_id, exercise_id, questioner_id, question, questioner_share, question_date)
          VALUES (?, ?, ?, ?, ?, ?, ?)"""
        
        return self.execute(sql, (course_id, assignment_id, exercise_id, questioner_id, question, questioner_share, get_current_datetime()))

    def get_question(self, question_id):
        sql = '''SELECT *
          FROM questions
          WHERE question_id = ?'''

        result = self.fetchone(sql, (question_id,))

        if result:
            question_dict = dict(result)
            question_dict["question_date"] = localize_datetime(question_dict["question_date"])
            if question_dict["answer_date"]:
                question_dict["answer_date"] = localize_datetime(question_dict["answer_date"])

            return question_dict

    def get_questions(self, course_id):
        sql = '''SELECT q.question_id,
                        q.course_id,
                        q.assignment_id,
                        a.title AS assignment_title,
                        q.exercise_id,
                        e.title AS exercise_title,
                        q.questioner_id,
                        u1.name AS questioner_name,
                        q.question,
                        q.question_date,
                        q.answerer_id,
                        u2.name AS answerer_name,
                        q.answer,
                        q.answer_date
          FROM questions q
          INNER JOIN assignments a ON q.assignment_id = a.assignment_id
          INNER JOIN exercises e ON q.exercise_id = e.exercise_id
          INNER JOIN users u1 ON q.questioner_id = u1.user_id
          LEFT JOIN users u2 ON q.answerer_id = u2.user_id
          WHERE q.course_id = ?
            AND a.visible = TRUE
            AND e.visible = TRUE
          ORDER BY q.question_date DESC'''

        results = []
        for row in self.fetchall(sql, (course_id,)):
            question_dict = dict(row)

            question_dict["question"] = question_dict["question"] if len(question_dict["question"]) <= 100 else question_dict["question"][:97].rstrip(" ") + "..."

            question_dict["answer"] = "" if not question_dict["answer"] else (question_dict["answer"] if len(question_dict["answer"]) <= 100 else question_dict["answer"][:97].rstrip(" ") + "...")

            question_dict["question_date"] = localize_datetime(question_dict["question_date"])
            if question_dict["answer_date"]:
                question_dict["answer_date"] = localize_datetime(question_dict["answer_date"])

            results.append(question_dict)

        return results

    def answer_question(self, question_id, question, question_modified, answerer_id, answer, answerer_share):
        sql = """UPDATE questions SET
  question = ?,
  question_modified = ?,
  answerer_id = ?,
  answer = ?,
  answerer_share = ?,
  answer_date = ?
WHERE question_id = ?"""

        self.execute(sql, (question, question_modified, answerer_id, answer, answerer_share, get_current_datetime(), question_id))

    def get_answered_questions(self, course_id, assignment_id, exercise_id, user_id):
        sql = '''SELECT question,
            answer,
            questioner_id,
            question_modified
          FROM questions
          WHERE course_id = ?
            AND assignment_id = ?
            AND exercise_id = ?
            AND answer IS NOT NULL
            AND questioner_share = 1
            AND answerer_share = 1
          ORDER BY question_id'''

        questions = []
        for row in self.fetchall(sql, (course_id, assignment_id, exercise_id)):
            questions.append((row["question"], row["answer"], row["questioner_id"] == user_id, row["question_modified"]))

        return questions
    
    def delete_question(self, question_id):
        sql = '''DELETE FROM questions
                 WHERE question_id = ?'''

        self.execute(sql, (question_id,))