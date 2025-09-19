import os
import sys
from datetime import datetime, timedelta
import glob
from dotenv import load_dotenv
import json

import re
from utils import ( get_last_modified_time,
				 	get_last_accessed_time,
				 	set_last_modified_time,
					set_last_accessed_time,
				  )
from tag_substitutions import ntfy_emojis

load_dotenv()

__NTFY_URL__ = os.getenv("ntfy_url", default="ntfy.sh/")
__NTFY_TOPIC__ = os.getenv("ntfy_topic", default="obsidiantaskstest")
__NTFY__TOKEN__ = os.getenv("ntfy_token", default="")

__TASK_FILES__ = [os.path.expanduser(f) for f in json.loads(os.getenv("task_files"))]
__LASTCHECK__ = get_last_accessed_time(__file__)
__POST_INTERVAL__ = timedelta(seconds=int(os.getenv("post_interval", default=3600)))
__DAY_START__ = os.getenv("post_interval", default="08:00")
__CHECK_INTERVAL__ = timedelta(seconds=int(os.getenv("check_interval", default=300)))

now = datetime.now()



def list_files():
	filelist = []
	for pattern in __TASK_FILES__:
		matching_files = glob.glob(pattern)
		if len(matching_files) > 0:
			for file in matching_files:
				modified = get_last_modified_time(file)
				if __LASTCHECK__ - modified < __CHECK_INTERVAL__:
					filelist.append(file)
	return filelist



def list_tasks(filelist):
	tasklist = []

	for file in filelist:
		title = file[str(file).rfind("/")+1:file.rfind(".md")]
		# print(title)
		with open(file, "r") as f:
			lines = f.readlines()
			for line in lines:
				if "#task" in line \
				and ("- [ ]" in line or "- [/]" in line) \
				and ('📅' in line or '⏳' in line or'🛫' in line):
					line = line.strip()
					task = parse_task(title, line)
					if task is not None:
						tasklist.append(task)

	return tasklist



def parse_task(title, line):
	fields = {
	'#task': 'task',
	'🆔': 'id',
	'📅': 'due_date',
	'⏳': 'scheduled_date',
	'🛫': 'start_date',
	'🔺': 'priority_highest',
	'⏫': 'priority_high',
	'🔼': 'priority_medium',
	'🔽': 'priority_low',
	'⏬': 'priority_lowest',
	'🔁': 'recurring',
	'➕': 'created_date',
	'⛔': 'depends_on_id',
	'🏁': 'on_completion',
	'⌚': 'time',
	'🏷️': 'tag',
	'📁': 'file',
	'🗺️': 'map',
	}
	pattern = f"({'|'.join(map(re.escape, fields.keys()))})"
	line = line.strip().replace("- [ ]", "").replace("- [/]", "")
	parts = re.split(pattern, line)
	parts = [p.strip() for p in parts]
	if parts[0]=="":
		parts = parts[1::]

	parts.remove("#task")

	# print(parts)

	if '📅' in parts:
		due_date = parts[parts.index('📅')+1]
		parts.remove('📅')
		parts.remove(due_date)
		if '⌚' in parts:
			time = parts[parts.index('⌚')+1]
			due_date = due_date + " " + time
			due_date = datetime.strptime(due_date, "%Y-%m-%d %H:%M")
		else:
			due_date = datetime.strptime(due_date, "%Y-%m-%d")
	else:
		due_date = datetime.fromtimestamp(0)
	
	if '⏳' in parts:
		scheduled_date = parts[parts.index('⏳')+1]
		parts.remove('⏳')
		parts.remove(scheduled_date)
		if '⌚' in parts:
			time = parts[parts.index('⌚')+1]
			scheduled_date = scheduled_date + " " + time
			scheduled_date = datetime.strptime(scheduled_date, "%Y-%m-%d %H:%M")
		else:
			scheduled_date = datetime.strptime(scheduled_date, "%Y-%m-%d")
	else:
		scheduled_date = datetime.fromtimestamp(0)
	
	if '🛫' in parts:
		start_date = parts[parts.index('🛫')+1]
		parts.remove('🛫')
		parts.remove(start_date)
		if '⌚' in parts:
			time = parts[parts.index('⌚')+1]
			start_date = start_date + " " + time
			start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
		else:
			start_date = datetime.strptime(start_date, "%Y-%m-%d")
	else:
		start_date = datetime.fromtimestamp(0)

	if '⌚' in parts:
			time = parts[parts.index('⌚')+1]
			parts.remove('⌚')
			parts.remove(time)

	try:
		soonest_date = min(
			dt for dt in [due_date, scheduled_date, start_date]
			if now < dt <= now + __POST_INTERVAL__
		)
	except ValueError:
		soonest_date = None
		return None

	priority = 3
	if '⏬' in parts:
		priority = 1
	elif '🔽' in parts:
		priority = 2
	elif '⏫' in parts:
		priority = 4
	elif '🔺' in parts:
		priority = 5

	print(parts)
	message = ' '.join(parts)
	return (title, message, priority, soonest_date)

def read_scheduled_notifications():
	import requests
	ntfy_messages = []
	headers = {
		"Authorization": f"Bearer {__NTFY__TOKEN__}",
		"Accept": "application/json",
	}
	response = requests.get("".join([__NTFY_URL__, __NTFY_TOPIC__, "/json?poll=1&sched=1"]), headers=headers)
	for line in response.iter_lines():
			if not line:
				continue
			line = json.loads(line)
			ntfy_messages.append(line)

	filtered = [item for item in ntfy_messages if item['event'] == 'message' and item['time'] >= now.timestamp()]
	print(filtered)
	# print(ntfy_messages)


def dispatch_notification(task):
	pass




def main():
	filelist = list_files()
	if len(filelist) <= 0:
		print("No files to list tasks from! Exiting...")
		sys.exit(0)

	tasklist = list_tasks(filelist)
	print(tasklist)
	if len(tasklist) <= 0:
		print("No tasks to send reminders for! Exiting...")
		sys.exit(0)
	set_last_accessed_time(__file__, now)
	# for debugging
	for file in filelist:
		set_last_modified_time(file, now)



if __name__ == "__main__":
	# main()
	read_scheduled_notifications()