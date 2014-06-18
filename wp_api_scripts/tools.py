# -*- coding: utf-8  -*-

import datetime

###
# debug print to standart or custom file
###
def debug_print(data, file_name="debug_print_file"):
    try:
        old_data = open(file_name, "r").read()
    except:
        old_data = ""
    try:
        open(file_name, "w").write(get_date() + " " + get_time() + " | " + data + "\n" + old_data)
    except:
        # nothing
        x = 0


###
# date & time
###
def get_date():
    now_datetime = datetime.datetime.now()
    now_date = now_datetime.strftime("%d.%m.%y")
    return now_date

def get_time():
    now_datetime = datetime.datetime.now()
    now_time = now_datetime.strftime("%H:%M:%S")
    return now_time


if __name__ == "__main__":
    print("don't call this file!")
    debug_print("ACHTUNG! Try to run tools.py")