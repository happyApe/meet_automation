# My-Google-Meet-Manager

### For scheduling : 

if using crontab (Linux) :

```
# Sets display environment variable for crontab so that selenium works as without it chrome wont open
# to find display number, run 
# env | grep 'DISPLAY'
DISPLAY=:1
# For setting environment for crontab so that pulseaudio works
# here 1000 is the usr_id
# to get usr_id, run : echo $UID
XDG_RUNTIME_DIR="/run/user/1000"

# It also creates a "meet_manager.log" in home directory
32 8-16 * * 1-5 cd /home/<user>/<path_to_repo>/meet_automation && /usr/bin/python3 /home/<user>/<path_to_repo>/meet_automation/my_google_meet_manager.py >> /home/<user>/meet_manager.log 2>&1 

```

otherwise you can use [schedule_it.py](https://github.com/happyApe/meet_automation/blob/master/schedule_it.py)
