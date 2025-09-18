import os
from datetime import datetime, timedelta

def get_last_modified_time(filepath):
	try:
		timestamp = os.path.getmtime(filepath)
		last_modified_datetime = datetime.fromtimestamp(timestamp)
		return last_modified_datetime
	except FileNotFoundError:
		print(f"Error: The file '{filepath}' was not found.")
	except Exception as e:
		print(f"An error occurred: {e}")

def get_last_accessed_time(filepath):
	try:
		timestamp = os.path.getatime(filepath)
		last_accessed_datetime = datetime.fromtimestamp(timestamp)
		return last_accessed_datetime
	except FileNotFoundError:
		print(f"Error: The file '{filepath}' was not found.")
	except Exception as e:
		print(f"An error occurred: {e}")


def set_last_accessed_time(filepath, time):
	try:
		access_time = os.path.getatime(filepath)
		os.utime(filepath, (time.timestamp(), access_time))
	except Exception as e:
		print(f"Failed to update the file timestamp: {e}")

def set_last_modified_time(filepath, time):
	try:
		modify_time = os.path.getmtime(filepath)
		os.utime(filepath, (time.timestamp(), modify_time))
	except Exception as e:
		print(f"Failed to update the file timestamp: {e}")