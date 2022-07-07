import schedule
import time
from icmplib import ping, NameLookupError
from fritzconnection import FritzConnection

# before running this script please execute
# pip install schedule icmplib fritzconnection

ROUTER_IP = '192.168.178.1'
PING_EVERY_N_MINUTES = 5
WEB_SITES = ['www.google.com', 'www.facebook.com', 'www.instagram.com']

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
    for url in WEB_SITES:
        print(f'pinging {url}')
        if website_isalive(url):
            print('Connection is OK')
            return

    # if all are dead
    fc = FritzConnection(address=ROUTER_IP)
    fc.reconnect()  # get a new external ip from the provider


schedule.every(PING_EVERY_N_MINUTES).minutes.do(check_if_connection_is_alive)
schedule.every(1).minute.do(print_dot)

print('Starting scheduler')

schedule.run_all()
while True:
    schedule.run_pending()
    time.sleep(1)  # sleep for 100ms
