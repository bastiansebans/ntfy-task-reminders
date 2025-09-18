# Obsidian tasks + NTFY
This simple script combines Obsidian's Tasks plugin and a [ntfy](https://github.com/binwiederhier/ntfy) instance introducing reminder notifications.

## How to use

1. create a `.env` file in the repository folder with variables for your ntfy server address, the topic, token and files to read tasks from. `task_files` can be a list of any wildcards recognisible by `glob` python package.
```bash
ntfy_url="https://ntfy.example.com/"
ntfy_topic="myreminders"
ntfy_token="tk_0123456789"
task_files=["~/obsidian/tasks/*.md"]
post_interval=3600
day_start=09:00
```
2. Setup the cron task executing the script, e.g. every 5 minutes. As a first step the script reads the last accessed time for each file listed in the `.env` file. If it hasn't been modified since the last check, the script exits.
3. The task will only get recognised if it is unchecked (`- [ ]`) or in progress (`- [/]`), has a global filter `#task`, and has at least one date (📅/⏳/🛫). In case of no time specified, time will be added from a `day_start` variable (in "HH:MM" format) to prevent notifications from coming exatly at midnight.  
4. Ntfy server does not allow deletion or modification of once posted notifications. Hence, the script waits until `post_interval` seconds to post the task to the ntfy server. This 'last minute' approach allows edits of the tasks and only submits them much later when the probability of edits is low.
5. To prevent resubmitions of the task, the 🆔 will be replaced with ntfy's notification ID.

### Syntax
The syntax this script recognises follows the obsidian task's plugin syntax. Each line satisfying requirements from (3.) will be split by the keywords/Emojis:

| Emoji | Name              | Function                                                             |
|-------|-------------------|----------------------------------------------------------------------|
| #task | task message      | The message of the task; markdown will be preserved _(Required)_     |
| 🆔    | id                | Unique identifier for the task.                                      |
| 📅    | due date          | Date by which the task should be completed.                         |
| ⏳    | scheduled date    | Date when the task is scheduled to begin.                           |
| 🛫    | start date        | Date when the task actually starts.                                 |
| 🔺    | priority highest  | Highest priority level.                                              |
| ⏫    | priority high     | High priority level.                                                 |
| 🔼    | priority medium   | Medium priority level.                                               |
| 🔽    | priority low      | Low priority level.                                                  |
| ⏬    | priority lowest   | Lowest priority level.                                               |
| ~~🔁~~    | ~~recurring~~      | ~~Indicates the task recurs on a schedule.~~                        |
| ➕    | created date      | Date the task was created. _(Ignored)_                              |
| ⛔    | depends on id     | Task dependency (another task this one depends on). _(Ignored)_     |
| 🏁    | on completion     | Task or action to trigger upon completion. _(Ignored)_              |


Additionally, the standard task syntax can be extended by these fields to match ntfy functionality:

| Emoji | Name   | Function                                                             |
|-------|--------|----------------------------------------------------------------------|
| ⌚    | Time   | Time of day to send out notification. Uses soonest future date.     |
| 📁    | File   | Path in quotes to attachement file to send out with notification.  |
| 🏷️    | Tag    | Additional emojis to use as ntfy notification [tags](https://docs.ntfy.sh/publish/#tags-emojis) |
| 🗺️    | geo    |  Links to open in maps |


### Not yet implemented features 
 - Recurring tasks
