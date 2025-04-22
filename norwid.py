from dotenv import load_dotenv
import os
import sys
import datetime
from dateutil import relativedelta


required_variables = ['HEARTBEAT_FILE', 'THRESHOLD']
load_dotenv()


def check_required_variables():
    for var in required_variables:
        if var not in os.environ:
            print('One of required variables is missing!', file=sys.stderr)
            exit(1)


def check_heartbeat():
    heartbeat_time = datetime.datetime.fromtimestamp(os.path.getmtime(os.getenv('HEARTBEAT_FILE')))
    current_time = datetime.datetime.now()
    time_difference = relativedelta.relativedelta(current_time, heartbeat_time)
    time_difference_in_months =  time_difference.years * 12 + time_difference.months
    print(time_difference_in_months)
    if time_difference_in_months > int(os.getenv('THRESHOLD')):
        notify()


def notify():
    print('Threshold exceeded')

if __name__ == '__main__':
    check_required_variables()
    check_heartbeat()