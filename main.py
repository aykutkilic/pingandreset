import schedule
import time
import datetime
from icmplib import ping, NameLookupError
from fritzconnection import FritzConnection
from fritzconnection.lib.fritzstatus import FritzStatus
from pushbullet import Pushbullet
import os

# before running this script please execute
# pip install schedule icmplib fritzconnection pushbullet.py
# set PUSHBULLET_API_KEY=<your api key here>

ROUTER_IP = '192.168.178.1'
PING_EVERY_N_MINUTES = 5
DELAY_AFTER_RESET_MIN = 5
RESET_EVERYDAY_AT = None
WEB_SITES = ['www.google.com', 'www.facebook.com', 'www.instagram.com']
PUSHBULLET_API_KEY = os.environ.get('PUSHBULLET_API_KEY')
PUSHBULLET_MSG_TITLE = 'Router failure'
REBOOT_OVER_RECONNECT = True

pushBulletApi = Pushbullet(PUSHBULLET_API_KEY)
lastResetTime = None


def push_note(title, body):
    global pushBulletApi
    push = pushBulletApi.push_note(title, body)


def website_isalive(url):
    try:
        return ping(url).is_alive
    except NameLookupError as e:
        print(f'Invalid URL {url}')


def print_dot():
    print('.', end='')


def check_if_connection_is_alive():
    global WEB_SITES
    global ROUTER_IP

    print('Checking if connection is OK')
    status = FritzStatus(address=ROUTER_IP)
    external_ip = '??'
    if status is not None:
        external_ip = status.external_ip

    print(f'Current external ip={external_ip}')

    for url in WEB_SITES:
        print(f'pinging {url}')
        if website_isalive(url):
            print('Connection is OK')
            return

    # if all are dead
    print('Connection is dead')
    now = datetime.datetime.now()
    if lastResetTime is not None:
        delta = (now - lastResetTime).total_seconds() / 60.0
        if delta <= DELAY_AFTER_RESET_MIN:
            print(f'Skipping reset as dt is {delta}<{DELAY_AFTER_RESET_MIN}')
            return

    fc = FritzConnection(address=ROUTER_IP)
    action = 'Reboot' if REBOOT_OVER_RECONNECT else 'Reconnect'
    message = f'{action}ing router at address {ROUTER_IP}'

    if REBOOT_OVER_RECONNECT:
        fc.reboot()  # reboot the router
    else:
        fc.reconnect()  # get a new external ip from the provider

    print(message)
    if PUSHBULLET_API_KEY is not None:
        push_note(PUSHBULLET_MSG_TITLE, message)


schedule.every(PING_EVERY_N_MINUTES).minutes.do(check_if_connection_is_alive)
schedule.every(1).minute.do(print_dot)
if RESET_EVERYDAY_AT is not None:
    schedule.every().day.at(RESET_EVERYDAY_AT).do(check_if_connection_is_alive)

print('Starting scheduler')

schedule.run_all()
while True:
    schedule.run_pending()
    time.sleep(100)  # sleep for 100ms
