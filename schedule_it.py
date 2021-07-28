import schedule
import time
import subprocess
import datetime

def job():
    proc = subprocess.Popen(["python3","my_google_meet_manager.py"],stdout = subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    stdout, stderr = proc.communicate()
    print(stdout.decode())
    print(stderr.decode())


# Run job from Mon to Fri every hour from 8:30-4:30

schedule.every().day.hour.at(":30").do(job)

while True : 
    curr_time = datetime.datetime.now()
    curr_time = curr_time.strftime('%H:%M')
    print(curr_time)
    if curr_time == "12:30":
        print("Sleeping for 50 minutes..")
        time.sleep(3000)
    schedule.run_pending()
    time.sleep(5)
