<h1 align="center"> My-Google-Meet-Manager </h1>

<p align="center">
  <img src="imgs/bot.jpg">
</p>

### Setup Instructions : 



- **Install Required Packages :**

    ```python
    pip install -r requirements.txt
    ```
    
- Requires [**chromedriver**](https://chromedriver.chromium.org/downloads)

    > Setup instructions and guide for Linux/Unix based can be found [here](https://christopher.su/2015/selenium-chromedriver-ubuntu/)

    
    
- **Find all the google meet links from google classrooms that you are joined to**, 

    - If you have a single classroom to be entered, run the following command

        ```python
        python3 my_google_meet_manager.py -a 
        ```
        > This will Add a single classroom based on the details you provide and automatically scrapes the meet link if available

    - If you want to add google classroom details in bulk, use the following tag

        ```python
        python3 my_google_meet_manager.py -b 
        ```
        > This gives bulk addition functionality, and automatically scrapes the classroom link from given **class_details.txt** file to find the meet link

        **Requires a class_details.txt** to be present 
        
        class_details.txt structure ( each column seperation by ; ) -> 

        <class_code> ; <course_code> ; <classroom_link>

    **The above two command results in generation fo class_schedule.csv file**

- **For changing the details of a classroom, run the following command**

    ```python
    python3 my_google_meet_manager.py -c 
    ```
    > This changes details of a classroom from given menu of class_schedule.csv

- **For timetable creation, run the following command**

    ```python
    python3 my_google_meet_manager.py -t 
    ```
    > This first asks for (one or two letter) codes of your classes, just like in a Timetable to represent a course

    > Then asks for your Timetable for each day from Mon-Fri from 8:30-5:30 

    > Finally generates a timetable.csv which has the timetable schedule used for running the main part of the script



### Running the script : 

    The script will ask you to login once only and then it stores all the cookies of your automated browser to folder named selenium created
    So from next time, you don't need to login again

   ```python
    python3 my_google_meet_manager.py
   ```

   > Running with no tags 

   > Fetches current day and time and joins respective google meet link via browser, also turns your microphone and camera off 

### For scheduling : 

- **If using crontab (Linux)** :

  > run the following command : 
  ```
  crontab -e
  ```
  > enter the following commmands accordingly : 

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

- **Otherwise you can use [schedule_it.py](https://github.com/happyApe/meet_automation/blob/master/schedule_it.py)**

### Attend for me : 

You can use the [attend_for_me.py](https://github.com/happyApe/meet_automation/blob/master/attend_for_me.py) to have a the script listen in background
and notify you whenever your name is called 

**Setup steps**:

- First, run the script with **-s** tag to setup the name list which consists of closely sounding words to your name

    ```python
    python attend_for_me.py -s 
    ```
    > This will generate a probable_names.txt file, which will contain those closely sounding names 

- Now, run the script with no tags whenver you are busy to attend

    ```python
    python attend_for_me.py 
    ```
    > This will notify you with notification (Linux/MacOs) and play a siren sound along with speech output 

