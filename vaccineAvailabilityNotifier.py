#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import timedelta, date as dt
import json
import logging
import requests
import time
from decouple import config
import userNotifier

headers = {'user-agent': 'temp'}

AGE = config('AGE')
PINCODE = config('PINCODE')
EMAIL = config('EMAIL')
APPLICATION_PASSWORD = config('APPLICATION_PASSWORD')


def get_logger(
        LOG_FORMAT='%(asctime)s - %(levelname)s - %(message)s',
        LOG_NAME='',
        LOG_FILE_INFO='VaccineNotifier.log'):
    log = logging.getLogger(LOG_NAME)
    log_formatter = logging.Formatter(LOG_FORMAT)
    file_handler_info = logging.FileHandler(LOG_FILE_INFO, mode='a+')
    file_handler_info.setFormatter(log_formatter)
    file_handler_info.setLevel(logging.DEBUG)
    log.setLevel(logging.DEBUG)
    log.addHandler(file_handler_info)
    return log


def main():
    logger = get_logger()
    try:
        check_availability()
    except Exception as e:
        logger.error("An error has occurred while checking the availability of slot : {}".format(e))


def check_availability():
    dates_list = fetch_next_10_days();
    for date in dates_list:
        get_slots_for_date(date)
    trigger_main()


def fetch_next_10_days():
    start_date = dt.today()
    number_of_days = 10
    date_list = []
    for day in range(number_of_days):
        date = start_date + timedelta(days=day)
        date_list.append(date.strftime("%d%m%Y"))
    return date_list


def get_slots_for_date(date):
    logger = get_logger()
    try:
        COWIN_API = (
            """https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={}&date={}""".format(
                PINCODE, date))
        response = requests.get(url=COWIN_API, headers=headers)
        content = json.loads(response.content)
        if content['centers'] != 0:
            for center in content['centers']:
                for session in center['sessions']:
                    min_age_limit = session['min_age_limit']
                    available_capacity = session["available_capacity"]
                    if min_age_limit <= int(AGE) & int(available_capacity) > 0:
                        userNotifier.notifyMe(json.loads(json.dumps(center)), EMAIL,
                                              APPLICATION_PASSWORD)
                        exit(1)
    except Exception as e:
        logger.error("An error has occurred while getting the valid slots : {}".format(e))


def trigger_main():
    time.sleep(120)
    main()


if __name__ == '__main__':
    main()
