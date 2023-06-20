import bs4
import requests
import os
import time
import datetime
import re
import json
import traceback

from enum import Enum
from dotenv import load_dotenv

load_dotenv()

from emailer import sendMessage

class NotificationType(Enum):
    ERROR = 1
    CHANGE = 2
    NO_CHANGE = 3

CALL_COUNT_LOG = 'callCount.log'
RESERVE_COUNT_LOG = 'reserveCount.log'
NOTIFY_LOG = 'notify.log'

CHECKING_FREQUENCY_SECONDS = 30*60 
NO_CHANGE_NOTIF_FREQUENCY_SECONDS = 24*60*60

DEV_RECIEVERS = json.loads(os.getenv('DEV_RECIEVERS'))
CHANGE_RECIEVERS = json.loads(os.getenv('CHANGE_RECIEVERS'))

URL = 'https://www.dwyerstorage.com/4863-nw-lake-road-camas-wa-98607'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
}

TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

def getButtons(url):
    r=requests.get(url, headers=HEADERS)
    soup = bs4.BeautifulSoup(r.content, 'html5lib')
    return soup.find_all('button')

def countButtonsContainingString(buttons, string):
    count = 0

    for b in buttons:
        for child in b.children:
            if (type(child) is bs4.element.NavigableString):
                if (string in child.string):
                    count += 1
    return count

def getLastCount(log):
    (_, m) = peekLog(log)
    if m == '':
        return 4
    else:
        return int(m)
    
def log(fileName, string):
    time_stamp = datetime.datetime.fromtimestamp(time.time()).strftime(TIME_FORMAT)

    f = open(fileName, "a")  # append mode
    f.write(f'[{time_stamp}] {string}\n')
    f.close()
  
def peekLog(fileName):
    try: 
        with open(fileName, 'rb') as f:
            try:  # catch OSError in case of a one line file 
                f.seek(-2, os.SEEK_END)
                while f.read(1) != b'\n':
                    f.seek(-2, os.SEEK_CUR)
            except OSError:
                f.seek(0)
            last_line = f.readline().decode()
            #remove timestamp
            if (last_line == ""):
                return (0, "")
            timestamp_str = last_line[last_line.find("[")+1:last_line.find("]")]
            timestamp = datetime.datetime.strptime(timestamp_str, TIME_FORMAT).timestamp()
            msg = re.sub(r'\[.*\]', '', last_line).strip()
            return (timestamp, msg)
    except FileNotFoundError:
        return (0, "")
    
def notify(notifType, err=None):

    subject, body, recievers = None, None, None
    if (notifType == NotificationType.CHANGE):
        recievers = CHANGE_RECIEVERS
        subject = '😱🚨🔔 Dwyerstorage.com changed!'
        body = f"""Hello,

I noticed a difference in the amount of call buttons on the dwyerstorage website. There may be a suitable storage spot available!
Check {URL} now!

Best,
Zawie's Bot"""
    elif (notifType == NotificationType.NO_CHANGE): 
        recievers = DEV_RECIEVERS
        subject = '✅ No changes detected on Dwyerstorage.com'
        body = f"""Hello,

No aciton required. This is just a health check informing you that no changes were detected on dwyerstorage site recently.
The site being monitored is {URL}.

Best,
Zawie's Bot"""
    elif (notifType == NotificationType.ERROR):
        recievers = DEV_RECIEVERS
        subject = '❌ Dwyerstorage monitor encountered an error!'
        body = str(err)
    else:
        raise Exception("invalid notifType")
    
    print(f"Attempting {notifType.name} notification!")

    sendMessage(recievers, subject=subject, body=body)

    log(NOTIFY_LOG, notifType.name)

sendMessage(DEV_RECIEVERS, 
    subject="🚀 Dwyerstorage Monitor is Starting", 
    body=f"""Hello,

This email is to notify you that Dwyerstorage monitor is starting! You should recieve an email when a change is detected and a health check every {NO_CHANGE_NOTIF_FREQUENCY_SECONDS} seconds.

Best,
Zawie's Bot"""
)

while True:
    try:     
        buttons = getButtons(URL)

        oldReserveCount = getLastCount(RESERVE_COUNT_LOG)
        newReserveCount = countButtonsContainingString(buttons, "Reserve")
        log(RESERVE_COUNT_LOG, newCallCount)

        oldCallCount = getLastCount(CALL_COUNT_LOG)
        newCallCount = countButtonsContainingString(buttons, "Call")
        log(CALL_COUNT_LOG, newCallCount)

        if (newCallCount < oldCallCount or newReserveCount > oldReserveCount):
            notify(NotificationType.CHANGE)
        else:
            (lastNotify, _) = peekLog(NOTIFY_LOG)
            if (time.time() - lastNotify > NO_CHANGE_NOTIF_FREQUENCY_SECONDS):
                notify(NotificationType.NO_CHANGE)
    except Exception as e:
        notify(NotificationType.ERROR, err=str(traceback.format_exc()))
    finally:
        time.sleep(CHECKING_FREQUENCY_SECONDS)