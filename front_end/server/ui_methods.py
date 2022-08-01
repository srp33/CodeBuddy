import os
import json
from helper import read_file

version = None
def get_version(handler):
	global version
	if version is None:
		version = read_file('../VERSION')
	return version