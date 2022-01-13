#!/home/momen/anaconda3/envs/python-zklib/bin/python
import json

from zk import ZK
from zk import attendance
from ZK import ParseConfig, configLogger
from datetime import datetime, date
import sys, getopt
import requests
import time
from time import mktime
import os
from pathlib import Path
import logging


def between_date(attend, start_date: datetime, end_date: datetime):
    return start_date < attend['attTime'] < end_date


long_codes = ["ip=", "start=", "end=", "type=", "uri="]


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    return obj


def init(argv):
    try:
        opts, args = getopt.getopt(argv, "i:s:e:t:u:", long_codes)
    except getopt.GetoptError:
        print(
            'test.py --ip <IP Address> --start <Date YYYY-mm-dd H:i> --end <Date YYYY-mm-dd H:i> --type <TYPE CHECKIN|CHECKOUT> --uri <URI url>')
        sys.exit(2)

    try:
        # Load the config
        config_path = Path(os.path.abspath(__file__)).parent / 'config.yaml'
        stream = open(config_path, 'r')

        # Parse config
        config = ParseConfig.parse(stream)

        # Setup connection
        checkin_config = config.get('checkin_device')
        checkout_config = config.get('checkout_device')
        start_date, end_date, uri = None, None, None

        for opt, arg in opts:
            if opt in ('-s', '--start'):
                start_date = datetime.fromtimestamp(mktime(time.strptime(arg, "%Y-%m-%d %H:%M")))
            elif opt in ('-e', '--end'):
                end_date = datetime.fromtimestamp(mktime(time.strptime(arg, "%Y-%m-%d %H:%M")))
            elif opt in ('-u', '--uri'):
                uri = arg

        checkin = ZK(ip=checkin_config.get('host'), port=checkin_config.get('port'))
        checkout = ZK(ip=checkout_config.get('host'), port=checkout_config.get('port'))

        print("Checkin Connecting... " + checkin_config.get('host'))
        checkin.connect()
        print("Checkin Connected " + checkin_config.get('host'))
        print("Checkin Getting Attendance")
        checkin_attendance_sheet = checkin.get_attendance()
        print("Checkin Attendance Gathered")
        checkin.disconnect()
        print("Checkin disconnected")

        print("Checkout Connecting... " + checkin_config.get('host'))
        checkout.connect()
        print("Checkout Connected " + checkout_config.get('host'))
        print("Checkout Getting Attendance")
        checkout_attendance_sheet = checkout.get_attendance()
        print("Checkout Attendance Gathered")
        checkout.disconnect()
        print("Checkout disconnected")

        attendance_sheet = []

        for attend in checkin_attendance_sheet:
            attendance_sheet.append({
                'userId': attend.user_id,
                'attTime': attend.timestamp,
                'type': 'CHECKIN'
            })

        for attend in checkout_attendance_sheet:
            attendance_sheet.append({
                'userId': attend.user_id,
                'attTime': attend.timestamp,
                'type': 'CHECKOUT'
            })

        print("Filtering")
        attendance_filtered = list(filter(lambda item: between_date(item, start_date, end_date), attendance_sheet))

        with open('json_data.json', 'w') as outfile:
            outfile.write(
                json.dumps(attendance_filtered, ensure_ascii=False, indent=4, sort_keys=True, default=json_serial))

        print(f"Sending " + str(len(attendance_filtered)) + " records")
        response = requests.post(uri, {'attendance': attendance_filtered})
        print(response)
        sys.exit()

    except Exception as error:
        print(error)
        sys.exit(1)


if __name__ == "__main__":
    init(sys.argv[1:])
