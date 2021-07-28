# A simple script to notify when your name is called (probably) by giving you a notification and playing siren sound and speaking up

# How to use ? 

# If running the script for the first time , use -s tag to setup 

# Whenever you are too busy to attend (Assuming this is the reason) 
# Just run this script on terminal and It will take care (probably)

import speech_recognition as sr
import os
import time
import argparse
import sys
from my_google_meet_manager import join_google_meet,speak_up

def setup():

    '''
    Function to setup the names by which the script will recognize and notify you
    '''

    file_exists = os.path.isfile('probable_names.txt')
    if file_exists : 
        print("probable_names.txt exists already, Please check if the probable names are correct")
        choice = input("Do you still want to create a new setup for names ? : [Y/n]")

        if (not choice) or choice.lower() == 'y':
            os.remove('probable_names.txt')

        else:
            print("Exiting the setup script")
            sys.exit()
        
    r1 = sr.Recognizer()
    print("Let's setup this..")

    names = []
    count = 0
    while count <3 :
        with sr.Microphone() as source:
            print("Speak your Name Boi ({})\n".format(count+1))
            r1.adjust_for_ambient_noise(source,duration=0.2)
            audio = r1.listen(source,phrase_time_limit = 5)
            text = r1.recognize_google(audio,language = 'en-IN',show_all=True)
            print(text)

            try:
                dict = text['alternative']

                for j in dict:
                    if(j['transcript'] not in names):
                        names.append(j['transcript'])
                count+=1
            except TypeError:
                print("Please speak again")

    count=1
    for i in names : 
        print("{}. ".format(count),i)
        count+=1

    print("\nPlease Enter the number corresponding to names you think are closest to your name")
    print("More names you choose, better the script will do")

    with open('probable_names.txt','w') as filename: 
        print("\nEnter numbers from the list corresponding to the names, Press 'q' to quit when you are done\n")
        temp_list = []
        while True:
            a = input('Number of the word : ')
            if a.lower() == 'q' : 
                break
            a = int(a)
            if a not in temp_list and a > 0 and a <= len(names) : 
                temp_list.append(a)
                filename.write((names[a-1]+'\n').lower())
            elif a in temp_list:
                print("The name exists in the file!")
            else:
                print("Invalid number entered!")

    print("The setup is completed!")


def keep_check():

    '''
    Function to keep checking and notify me whenever name (probably) is called 
    '''
    r1 = sr.Recognizer()

    file_exists = os.path.isfile('probable_names.txt')
    if not file_exists : 
        print("There is no file called probable_names.txt")
        print("Please run the script with -s tag to setup")
        sys.exit()

    with open('probable_names.txt') as filename:
        names = filename.read()
        
    names = names.split('\n')[:-1]
    print(names)

    # some counters to prevent filling up my notifications and speakers (:
    play_once = 0
    notify_twice = 0
    notify_twice_attendance = 0
    while True:
        with sr.Microphone() as source : 
            r1.adjust_for_ambient_noise(source, duration = 0.5)
            audio = r1.listen(source,phrase_time_limit = 3)
            text = r1.recognize_google(audio, language = 'en-IN', show_all=True)
            try : 
                dict = text['alternative']
                for i in dict:
                    s = i['transcript'].lower()
                    s = s.split(" ")
                    # print(s)
                    if any(word in names for word in s):
                        speak_up('Your Name is being called')
                        print("Looks like you are called")
                        if play_once != 1 : 
                            os.system('aplay ./sounds/alert_siren.wav')
                            play_once += 1
                        if notify_twice != 2: 
                            os.system('notify-send "You are called in meet probably! Return to meet!!"')
                            notify_twice +=1
                             
                    if 'attendance' in s : 
                        speak_up('Attendance!')
                        print("Attendance time",s)
                        if notify_twice_attendance != 2: 
                            os.system('notify-send "Attendance Time in class!"')
                            notify_twice_attendance+=1

            except Exception as e:
                continue
                   

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'Attend for me')
    parser.add_argument('-s','--setup', action = 'store_true',help = 'Setup the names by which it will notify ')
    args = parser.parse_args()

    if args.setup:
        # call the setup script
        setup()
    else : 
        # For testing
        # join_google_meet('meet link here')

        # Run the Recognizer 
        keep_check()

