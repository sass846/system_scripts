#!/usr/bin/env python3

import time
import subprocess
import logging

BATTERY_CAPACITY = "/sys/class/power_supply/BAT0/capacity"
PLUGGED = "/sys/class/power_supply/ACAD/online"
THRESHOLD_LOW = 30
THRESHOLD_CRITICAL = 15
THRESHOLD_HIGH = 90
AUDIO_LOW = "/home/stryder/Music/sfx/battery_low.ogg"
AUDIO_CRITICAL = "/home/stryder/Music/sfx/battery_critical.ogg"

def send_notification(message,urgency="--urgency=normal", audio="home/stryder/Music/sfx/normal.ogg"):
    subprocess.Popen(['notify-send',urgency,'--icon=dialog-information','\'Battery Notification\'',message])
    subprocess.Popen(['mpv',audio,'--really-quiet'])

def read_battery_capacity():
    try:
        with open(BATTERY_CAPACITY,"r") as file:
            capacity = int(file.read().strip())
        return capacity
    except (FileNotFoundError, PermissionError, ValueError) as e:
        logging.error(f"Error opening file {BATTERY_CAPACITY}: {e}")
        return -1

def read_ac_status():
    try:
        with open(PLUGGED,"r") as file:
            status = int(file.read().strip())
        return status
    except (FileNotFoundError, PermissionError, ValueError) as e:
        logging.error(f"Error opening file {PLUGGED}: {e}")
        return -1

def main():
    prev_ac_status = read_ac_status()
    low_flag = False
    critical_flag = False
    high_flag = False
    last_notification_time = time.time()

    while True:
        capacity = read_battery_capacity()
        ac_status = read_ac_status()

        current_time = time.time()
        if current_time - last_notification_time > 600:
            low_flag = False
            critical_flag = False
            high_flag = False

        if ac_status != prev_ac_status:
            if ac_status == 1:
                send_notification("Battery charging")
            else:
                send_notification("Discharging","--urgency=critical")

            prev_ac_status = ac_status

        if capacity < THRESHOLD_LOW and capacity > THRESHOLD_CRITICAL and ac_status == 0:
            send_notification(f"{capacity}% \nBatter low!!!\nPlease plug in your charger.","--urgency=critical",AUDIO_LOW)
            low_flag = True
            last_notification_time = current_time
        elif capacity < THRESHOLD_CRITICAL and ac_status == 0:
            send_notification(f"{capacity}% \nBattery critical!!!\nPlease plug in your charger.","--urgency=critical",AUDIO_CRITICAL)
            critical_flag = True
            last_notification_time = current_time
        elif capacity > THRESHOLD_HIGH and ac_status == 1:
            send_notification(f"{capacity}% \nBattery high!!!\nPlease unplug your charger.")
            high_flag = True
            last_notification_time = current_time


if __name__ == "__main__":
    logging.basicConfig(filename='battery_notify.log', level=logging.ERROR)
    main()

