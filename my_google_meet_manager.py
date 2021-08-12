#! /usr/bin/python3

# #! /home/voila/py3.6/bin/python

# My Google Classroom and Meet Manager 

# First fetches all the class schedules from timetable and will make a csv/txt file which has details :
# [Class Name] [Course Code] [Classroom Link] [Meet link]
# It then stores all classes (based on timetable code) with the Timestamps for whole week [Mon - Fri] as a csv/txt file    
# From the timetable based file, It will then open chrome browser (using selenium) Automatic login will be stored (just once need to login at very first time running
# this script) and then it will go to the respective classroom link and go to meet link or maybe directly go to meet link


# Usage : 
# python my_google_meet_manager.py -a => Adds a single classroom detail and automatically scrapes the meet link if available
# python my_google_meet_manager.py -b => Bulk addition of classroom and automatically scrapes the meet link from given txt file by name "class_details.txt" with ; seperation
# python my_google_meet_manager.py -c => Change details of a classroom from given menu of the class_schedule.csv file
# python my_google_meet_manager.py -t => Timetable creation, first asks codes for classrooms and then asks class schedule and saves to timetable.csv
# Without Tags:
# python my_google_meet_manager.py => 
        # Find the Day today and check timetable.csv file and then check time right now for today and based on that go to class_schedule.csv file to fetch the
        # meet link if there, then it runs a browser (selenium) and turnsoff microphone and camera and then joins the meet. It also speaks few of the steps 

# Extra : [DONE] add speaking functionality to inform me about joining which google meet classs
# Extra : add a way to answer on my behalf whenever my name gets called out in meeting 


import pdb
import bs4, requests
import os, sys
import smtplib,ssl
import argparse
import csv
import pandas as pd
import time
import math
import calendar
import datetime
from collections import defaultdict
import pyttsx3 # requires espeak package (sudo dnf/apt install espeak)

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import webbrowser


def get_meet_link(class_link):

    ''' 
    Function fetches the meet link from the given classroom link
    Have to use selenium as bs4 and requests can't handle the login part automatically
    '''
    chrome_options = Options()
    chrome_options.add_argument('user-data-dir=selenium')
    
    driver = webdriver.Chrome('/usr/bin/chromedriver',options = chrome_options)
    driver.get(class_link)

    driver.implicitly_wait(5)
    try : 
        # better than having xpath or css_selector to fetch meet link
        meet_link = driver.find_element_by_partial_link_text('meet.google.com')
        # print(meet_link.text)
        link = meet_link.text
    except : 
        link = 'None'

    if link == 'None':
        print("Meet link is not on google classroom meet link column..")
        print("Please run the script with -c tag to change the meet link to the one you find.")

    # meet_link.click()
    # time.sleep(5)
    time.sleep(2)
    driver.quit()
    return link

def add_to_class_schedule(class_name,course_code,class_link,meet_link):

    ''' 
    Function stores the classroom details to csv file 'class_schedule.csv'
    '''

    file_exists = os.path.isfile('class_schedule.csv')

    with open('class_schedule.csv','a',newline = '') as file : 
        fieldnames = ['Class Name', 'Course Code', 'Classroom Link', 'Meet Link']

        writer = csv.DictWriter(file,delimiter = ',', lineterminator = '\n',fieldnames = fieldnames)

        if not file_exists : 
            writer.writeheader()

        writer.writerow({'Class Name' : class_name,'Course Code' : course_code, 'Classroom Link' : class_link, 'Meet Link' : meet_link})

    print("\nSaving to file....")
    print("Class Schedule Updated!\n")

def duplicate_handler():

    ''' 
    Function to handle duplicate values in the csv file.
    Handles full duplicate rows and gives you choice to choose one of the rows 
    from same name possesing rows
    '''

    df = pd.read_csv('class_schedule.csv')

    # Returns True if whole row is duplicate
    any_duplicate_rows = df.duplicated().any()

    # If whole rows are duplicate then simply remove duplicates
    if any_duplicate_rows : 
        df.drop_duplicates(inplace = True)
        df.to_csv('class_schedule.csv',index = False)
        print("Duplicate Rows were removed....\n")

    df = pd.read_csv('class_schedule.csv')

    # Returns True if there any same names in Class Name column
    any_duplicate_names = df.duplicated(subset = ['Class Name']).any()

    if any_duplicate_names : 
        # Gives all duplicated values based on class name column
        print(df[df.duplicated(['Class Name'],keep = False)])
        duplicate_index = (df[df.duplicated(['Class Name'],keep = False)].index.values.tolist())
        print("\nIndex Numbers : ",duplicate_index)

        choice = int(input('Enter which row [index no] to keep in your class schedule : '))
        while choice not in duplicate_index:
            choice = int(input('Enter which row to keep in your class schedule : '))
        
        duplicate_index.remove(choice)
        df.drop(df.index[duplicate_index],inplace = True)
        df.to_csv('class_schedule.csv',index = False)

        print("\nAll other duplicate recipes were deleted ... \n")

def bulk_add_to_class_schedule():

    '''
    Function that fetches links from txt file 'class_details.txt' and adds them to 'class_schedule.csv' file
    '''

    file_exists = os.path.isfile('class_details.txt')
    if not file_exists : 
        print("No file : class_details.txt found, please either create a file with this name and add urls or use -a argument while running the script")
        print("Please use ' ; ' to seperate the Class Columns")
        sys.exit()
    if os.stat('class_details.txt').st_size == 0:
        print("File is empty.. please fill the class details and use ' ; ' for seperation")
        sys.exit()

    with open('class_details.txt','r') as file : 
        classrooms = file.read()
        print(classrooms)


    classrooms  = classrooms.split('\n')[:-1]
    classrooms = [x for x in classrooms if x ] # to remove empty strings from list caused by extra newlines in txt file
    # print(classrooms)
    print("\nAdding Classes to csv file....")

    for classroom in classrooms : 
        value = classroom.split(' ; ')
        print("Class Name :",value[0])
        print("Course Code :",value[1])
        print("Class Link : ",value[2])
        meet_link = get_meet_link(value[2])
        print("Meet Link : ",meet_link)
        add_to_class_schedule(value[0],value[1],value[2],meet_link)

    print("All Classes added!")

def change_in_classroom():

    ''' 
    Function to change details of a particular classroom from given displayed dataframe
    '''

    file_exists = os.path.isfile('class_schedule.csv')
    if not file_exists : 
        print("No file : class_schedule.csv found, please use -a argument for adding classrooms or use -b tag for bulk addition")
        sys.exit()
    if os.stat('class_schedule.csv').st_size == 0:
        print("File is empty.. please fill the class details using -a or -b tag")
        sys.exit()
    df = pd.read_csv('class_schedule.csv')

    print("\nClassroom details : ")
    print(df)
    index_range = df.index.values.tolist()

    choice = int(input("\nEnter the row [index no] which you wish to edit : "))
    while choice not in index_range : 
        choice = int(input("Enter the [index no] for row which you wish to edit : "))

    print()
    print(df.iloc[choice])
    print()

    print("Column Indexes : ")
    col_indexes = [df.columns.get_loc(c) for c in df.columns if c in df]
    print(col_indexes)

    column_chosen = int(input("Enter column index that you wish to modify : "))
    while column_chosen not in col_indexes : 
        column_chosen = int(input("Enter column index that you wish to modify : "))

    column_chosen = df.columns[column_chosen]

    new_value = input("Enter the new " + str(column_chosen) + " : ")
    df.loc[choice,column_chosen] = new_value
    print()
    print(df)
    print()

    print("Value Updated!")
    print("Saving to csv file...")
    df.to_csv("class_schedule.csv",index = False)
    print("Done.\n")

def generate_class_codes():
    ''' 
    Function asks to assign a Code (generally a Letter or two) as like in my college timetable for easy timetable creation
    Returns a dictionary with key as Class Name and value as Timetable Code.
    '''
    
 
    file_exists = os.path.isfile('class_schedule.csv')
    if not file_exists : 
        print("No file : class_schedule.csv found, please use -a argument for adding classrooms or use -b tag for bulk addition")
        sys.exit()
    if os.stat('class_schedule.csv').st_size == 0:
        print("File is empty.. please fill the class details using -a or -b tag")
        sys.exit()

    class_names = []
    with open('class_schedule.csv') as file:
        csv_reader = csv.reader(file,delimiter = ',')
        next(csv_reader) # skip header
        for row in csv_reader : 
            class_names.append(row[0])

    # print(class_names)

    timetable_codes = {}
    for name in class_names : 
        print("Enter code for" ,end  = ' ' )
        print(name, end = ' ')
        code = input(" : ")
        timetable_codes[name] = code

    # print(timetable_codes)
    return timetable_codes


def update_class_schedule(timetable_codes):
    ''' 
    Function to add a cloumn of timetable codes based on the class name from the class_schedule csv file
    '''
    file_exists = os.path.isfile('class_schedule.csv')
    if not file_exists : 
        print("No file : class_schedule.csv found, please use -a argument for adding classrooms or use -b tag for bulk addition")
        sys.exit()
    if os.stat('class_schedule.csv').st_size == 0:
        print("File is empty.. please fill the class details using -a or -b tag")
        sys.exit()

    print("\nAdding timetable codes to the class_schedule.csv file....")
    df = pd.read_csv('class_schedule.csv')
    df['Timetable Code'] = df['Class Name'].map(timetable_codes)
    df.to_csv('class_schedule.csv',index = False)
    time.sleep(3)
    print("\nTimeTable codes added as a column to class_schedule.csv file!\n\n")
    time.sleep(2)

 

def create_my_timetable(timetable_codes):
    '''
    Function to create my timetable from the dictionary of timetable codes and save timtable as timetable.csv file
    '''
    week_days = list(calendar.day_name)
    week_days = week_days[:-2]
    timings = ['08:30-09:20','09:30-10:20','10:30-11:20','11:30-12:20','13:30-14:20','14:30-15:20','15:30-16:20','16:30-17:20']
    # print(week_days)


    file_exists = os.path.isfile('timetable.csv')
    
    if file_exists : 
        # choose modify the existing file
        df = pd.read_csv('timetable.csv')
        print("\n Timetable : ")
        print(df)
        edit_choice = input("\nDo you wish to edit the given timetable ? [Y/N] : ")
        if edit_choice.lower() == 'y':
            index_range = df.index.values.tolist()
            choice = int(input("\nEnter the row [index no] which you wish to edit : "))
            while choice not in index_range : 
                choice = int(input("Enter the [index no] for row which you wish to edit : "))
            print()
            print(df.iloc[choice])
            print()

            print("Column Indexes : ")
            col_indexes = [df.columns.get_loc(c) for c in df.columns if c in df]
            print(col_indexes)

            column_chosen = int(input("Enter column index that you wish to modify : "))
            while column_chosen not in col_indexes : 
                column_chosen = int(input("Enter column index that you wish to modify : "))

            column_chosen = df.columns[column_chosen]

            new_value = input("Enter the new " + str(column_chosen) + " : ")
            df.loc[choice,column_chosen] = new_value
            print()
            print(df)
            print()
            print("Value Updated!")
            print("Saving to csv file...")
            df.to_csv("timetable.csv",index = False)
            print("Done.\n")
            sys.exit()

        else : 
            return


    print("\nEnter the schedule according to the given day : ")

    print("Enter the timtable codes according to timings")
    print("\nIf there is no class for a timing, press Enter\n")

    timetable_dict = defaultdict(dict)
    codes = [val for val in timetable_codes.values()]
    codes.append('')
    print("Class Codes :",codes,'\n')
    for day in week_days: 
        print("For",day)
        for timing in timings : 
            print("{:>20}".format(timing),end = ' ')
            class_time = input(" : ")
            while class_time not in codes:
                print("\nEnter class with in following class codes : " )
                print(codes,'\n')
                print("{:>20}".format(timing),end = ' ')
                class_time = input(" : ")

            timetable_dict[day][timing] = class_time

    # If to use premade timetable, uncomment the following
#     timetable_dict = {'Monday': {'8:30-9:20': 'A', '9:30-10:20': 'F', '10:30-11:20': 'E', '11:30-12:20': 'D', '1:30-2:20': 'BL', '2:30-3:20': 'BL', '3:30-4:20': '', 
#         '4:30-5:20': ''}, 'Tuesday': {'8:30-9:20': 'B', '9:30-10:20': 'A', '10:30-11:20': 'F', '11:30-12:20': 'E', '1:30-2:20': 'DL', '2:30-3:20': 'DL', '3:30-4:20': '', '4:30-5:20':
#              ''}, 'Wednesday': {'8:30-9:20': '', '9:30-10:20': 'B', '10:30-11:20': 'A', '11:30-12:20': 'F', '1:30-2:20': 'AL', '2:30-3:20': 'AL', '3:30-4:20': '', '4:30-5:20': ''}, 'Thursday': {'8:30-9:20': 'D', '9:30-10:20': '', '10:30-11:20': 'B', '11:30-12:20': 'F', '1:30-2:20': 'EL', '2:30-3:20': 'EL', '3:30-4:20': '', '4:30-5:20': ''}, 
#              'Friday': {'8:30-9:20': 'E', '9:30-10:20': 'D', '10:30-11:20': '', '11:30-12:20': '', '1:30-2:20': '', '2:30-3:20': '', '3:30-4:20': '', '4:30-5:20': ''}}
#     print(timetable_dict)
    print("")

        # Convert into pandas dataframe
    df = pd.DataFrame.from_dict(timetable_dict).T.rename_axis('Day').reset_index()
    print()
    print(df)
    print()

    print("Saving timetable to csv file...")
    df.to_csv('timetable.csv',index = False)
    print("Done!\n")


def get_day_and_time():

    '''
    Function to get the day today and current timeand return it
    '''
    today = datetime.datetime.now()
    curr_time = datetime.datetime.now()
    return today.strftime("%A"),curr_time.strftime('%H:%M') # Use %I instead of %H to get 12hr time format
    

def is_between(time,time_range):
    
    # print(time_now,time_range)
    # pdb.set_trace()
    if time_range[1] < time_range[0]:
        return time >= time_range[0] or time <= time_range[1]

    return time_range[0] <= time and time <= time_range[1]


def check_timetable(today,time_now):
    
    '''
    Function to get the class details of which to join based on current time and day from timetable.csv file
    '''

    df = pd.read_csv('timetable.csv')
    intervals = df.columns.values.tolist()[1:]
    start_times = [x[:x.find('-')] for x in intervals]
    end_times = [x[x.find('-')+1:] for x in intervals]
    # print(start_times)
    # print(end_times)

    print('\nTime now :',time_now)
    # print(is_between(time_now,(start_times[0],end_times[0])))

    for i,(s,e) in enumerate(zip(start_times,end_times)):

        # print(time_now,s,e)
        # print(is_between(time_now,(s,e)))
        if is_between(time_now,(s,e)):
            # If time now is between a class schedule interval return the class code for joining
            # print(df)
            class_code = df[df['Day']==today][intervals[i]].values[0]
            # To check if class_code is nan value or not 
            try : 
                if math.isnan(class_code):
                    class_code = "No class"
            except:
                pass
            print("Class code :",class_code)
            if class_code == "No class":
                   print("Looks like there is no class") 
            else:
                print("Joining Now for", s,"class")
            return class_code,0

        elif is_between(time_now,(end_times[i-1],start_times[i])):
            # If still time to join a class, print time to join and class code
            # print(time_now,end_times[i-1],start_times[i])
            time_now_datetime = datetime.datetime.strptime(time_now,'%H:%M')
            class_time_datetime = datetime.datetime.strptime(s,"%H:%M")
            diff = (class_time_datetime-time_now_datetime)

            class_code = df[df['Day']==today][intervals[i+1]].values[0]
            # To check if class_code is nan value or not 
            try : 
                if math.isnan(class_code):
                    class_code = "No class"
            except:
                pass
            print("Joining the class",class_code,"at",s,"in",diff)

            # Will send Waiting code and the time till joining 
            class_code = 'Waiting'
            return class_code,diff

  


def fetch_meet_link_for_class(class_code) : 

    ''' 
    Function to fetch the meet link for the class based on the given timetable/class code 
    '''

    df = pd.read_csv('class_schedule.csv')
    if class_code == 'No class':
        meet_link = class_code
        return meet_link

    meet_link = df[df['Timetable Code']==class_code]['Meet Link'].values.tolist()[0]

    return meet_link

def turn_off_mic_and_cam(driver):
    
    '''
    Function to turn off mic and cam of google meet
    '''

    # Turn off mic
    driver.implicitly_wait(10)
    try : 
        mic = driver.find_element_by_xpath('//*[@id="yDmH0d"]/c-wiz/div/div/div[9]/div[3]/div/div/div[2]/div/div/div[1]/div[1]/div/div[4]/div[1]/div/div/div/span/span/div/div[1]')
    except:
        mic = driver.find_element_by_xpath('//*[@id="yDmH0d"]/c-wiz/div/div/div[9]/div[3]/div/div/div[4]/div/div/div[1]/div[1]/div/div[4]/div[1]/div/div/div/span/span/div/div[1]/div')
    mic.click()
    speak_up("Mic turned off")
    print("Mic Turned off")

    # Turn off camera
    driver.implicitly_wait(10)
    time.sleep(1)
    try:
        cam = driver.find_element_by_xpath('//*[@id="yDmH0d"]/c-wiz/div/div/div[9]/div[3]/div/div/div[2]/div/div/div[1]/div[1]/div/div[4]/div[2]/div/div/span/span/div')
    except:
        cam = driver.find_element_by_xpath('//*[@id="yDmH0d"]/c-wiz/div/div/div[9]/div[3]/div/div/div[4]/div/div/div[1]/div[1]/div/div[4]/div[2]/div/div/span/span/div/div')
    cam.click()
    speak_up("Camera turned off")
    print("Camera Turned off")


def join_google_meet(meet_link):

    '''
    Function to join the google meet link
    '''
    chrome_options = Options()
    chrome_options.add_argument('user-data-dir=selenium')
    # To have the default chrome installation browser cookies.. but it requires the browser chrome to be 
    # closed before running the script otherwise an instance exists issue error comes up
    # So I recommend using the cookies from a custom folder like 'selenium' folder in this directory 
    # chrome_options.add_argument('user-data-dir=/home/waveandsmile/.config/google-chrome/')
    chrome_options.add_argument('--no-sandbox') # bypass OS security model
    # chrome_options.add_argument("--disable-dev-shm-usage") #overcome limited resource problems
    # chrome_options.add_argument('--disable-infobars')
    # chrome_options.add_argument('start-maximized')

	# Pass the argument 1 to allow and 2 to block
    chrome_options.add_experimental_option("prefs", { \
    "profile.default_content_setting_values.media_stream_mic": 1, 
    "profile.default_content_setting_values.media_stream_camera": 1,
    "profile.default_content_setting_values.geolocation": 1, 
    "profile.default_content_setting_values.notifications": 1,
    })
    # To keep running
    chrome_options.add_experimental_option("detach",True)
    
    driver = webdriver.Chrome('/usr/bin/chromedriver',options = chrome_options)
    driver.get(meet_link)
    time.sleep(1)
    speak_up("Turning mic and cam off")
    turn_off_mic_and_cam(driver)
    
    # Join the meet
    driver.implicitly_wait(20)
    print("Joining the meet..")
    speak_up("Joining meet")
    time.sleep(1)
    try: 
        join_it = driver.find_element_by_xpath('//*[@id="yDmH0d"]/c-wiz/div/div/div[9]/div[3]/div/div/div[2]/div/div/div[2]/div/div[2]/div/div[1]/div[1]/span/span')
    except:
        join_it = driver.find_element_by_xpath('//*[@id="yDmH0d"]/c-wiz/div/div/div[9]/div[3]/div/div/div[4]/div/div/div[2]/div/div[2]/div/div[1]/div[1]')

    join_it.click()
    speak_up("class joined")

def speak_up(text):
    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate',rate-60)
    engine.say(text)
    engine.runAndWait()

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description = 'Google Classroom and Meet Manager')
    parser.add_argument('-a','--add',action = 'store_true',help = 'Add a classroom with details [Class Name] [Course Code] [Classroom Link] [Meet link]')
    parser.add_argument('-b','--bulk',action = 'store_true',help = 'Bulk addition of classes from class_details.txt file')
    parser.add_argument('-c','--change',action = 'store_true',help = 'Change details of a classroom from the given menu it shows')
    parser.add_argument('-t','--timetable',action='store_true',help = 'Timetable creation, first asks codes for classrooms and then asks class schedule and saves to timetable.csv')
    args = parser.parse_args()
    
    if args.timetable:
        # Timtable codes generator by asking the user
        timetable_codes = generate_class_codes()
        # timetable_codes = {'DMDW': 'E', 'DMDW Lab': 'EL', 'IDAA': 'A', 'IDAA Lab': 'AL', 'Java': 'B', 'Java Lab': 'BL', 'FLAT': 'F', 'OS': 'D', 'OS Lab': 'DL', 'Economics': 'C'}   

        # update class schedule to now have a new column called TimeTable codes based on the generated class codes
        update_class_schedule(timetable_codes)
        create_my_timetable(timetable_codes)
        print("Run the script with no tags for joining class.")
        sys.exit()

    if args.change : 
        change_in_classroom()
        duplicate_handler()
        print("Run the script with no tags for joining class.")
        sys.exit()


    if args.bulk : 
        bulk_add_to_class_schedule()
        duplicate_handler()
        print("Run the script with no tags for joining class.")
        sys.exit()


    if args.add:
        class_name = input("\nEnter Class Name : ")
        course_code = input("Enter Course Code : ")
        class_link = input("Enter Google Classroom Link : ")
        # It will fetch the meet link from classroom link
        meet_link = get_meet_link(class_link)
        add_to_class_schedule(class_name,course_code,class_link,meet_link)
        duplicate_handler()
        print("Run the script with no tags for joining class.")
        sys.exit()

    else: 
        # Go to the meet link of the class based on the time schedule

        file_exists = os.path.isfile('class_schedule.csv')
        if not file_exists : 
            print("No file : class_schedule.csv found, please use -a argument for adding classrooms or use -b tag for bulk addition")
            sys.exit()
        if os.stat('class_schedule.csv').st_size == 0:
            print("File is empty.. please fill the class details using -a or -b tag")
            sys.exit()

        file_exists = os.path.isfile('timetable.csv')
        if not file_exists : 
            print("No file : timetable.csv found, please use -t argument for adding a timetable")
            sys.exit()
        if os.stat('timetable.csv').st_size == 0:
            print("File is empty.. please add timetable using -t argument")
            sys.exit()

        # Find the Day today and check timetable.csv file and then check time right now for today and based on that go to class schedule csv file
        # From there based on timetable codes go to the specific meet link if present there

        today,time_now = get_day_and_time()

        # For debugging set custom time_now
        # today = 'Monday'
        # time_now = '09:39'
 
        if int(time_now[:time_now.find(":")]) >= 17:
            print("Time now",time_now,"is way pass the schedule..")
            print("Run script tomorrow..")
            sys.exit()

        if today not in list(calendar.day_name)[:-2] : 
            print("Exiting")
            print("The program is for weekdays only and today sir is not a weekday!")
            sys.exit()
        # print(today,time_now)

        class_code,wait_time = check_timetable(today,time_now)

        # If in waiting, it will calculate time in seconds till join and will sleep for that period and then get the class code again
        if class_code == 'Waiting':
            if wait_time >= datetime.timedelta(seconds = 3000):
                print("Exiting")
                print("Waiting Time is equal or more than 50 minutes, Exiting the script")
                speak_up("Waiting Time is equal or more than 50 minutes, Exiting the script")
                sys.exit()
            

            print("Sleeping for",wait_time.seconds,"seconds")
            time.sleep(wait_time.seconds)
            # get time_now again
            today,time_now = get_day_and_time()
            # fetch the class code again
            class_code,wait_time = check_timetable(today,time_now)
            print(class_code)


        # Going to class_schedule.csv to fetch the meet link for that class
        meet_link = fetch_meet_link_for_class(class_code)
        # print(meet_link)

        if meet_link == class_code:
            print("No class right now according to schedule")
            sys.exit()

        if not meet_link.startswith('https'):
            print("Meet link not present")
            speak_up("There is no Meet Link to join.. Please add one")
            sys.exit()
        # Open the meet link
        speak_up("Joining the Class Code" + str(class_code))
        time.sleep(2)
        join_google_meet(meet_link)



