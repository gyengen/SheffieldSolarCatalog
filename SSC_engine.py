#!/usr/bin/env python

'''----------------------------------------------------------------------------

License:

    This program is free software: you can redistribute it and/or modify
    it. This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

    If you use this software (or a part of it) in your research, please cite
    the authors. For more information how to cite this work properly please
    visit the official webside. THANKS!

                            www.ssc.sheffield.ac.uk

cron_engine.py

    Advanced Python Scheduler (APScheduler) is a Python library that lets you
    schedule your Python code to be executed later, either just once or
    periodically. You can add new jobs or remove old ones on the fly as you
    please.

----------------------------------------------------------------------------'''

from apscheduler.scheduler import Scheduler
from datetime import datetime
import engine.engine
import logging
import os

__author__ = ["Gyenge, Norbert"]
__email__ = ["n.g.gyenge@sheffield.ac.uk"]

# SETUP -------------------------------------------------------------------'''

# STEP 1: Interval-based scheduling. This method schedules jobs to be run on
# selected intervals (in minutes).

interval = '5'

# STEP 2: Lag-time. The downloaded observations cannot be real-time because
# the JSOC and the ShARC services need time for publising data The lag-time
# defines a period of time between the present and the observations.

lag = 360

# STEP 2: Email address. The JSOC service requires a registred email address
# for downloading the observations. Please do not use this email address if
# you are not involved developing this software. Instead, use the official
# JSOC for validating your own email address.
# http://jsoc.stanford.edu/ajax/register_emvalidatedail.html

email = 'scc@sheffield.ac.uk'

# SETUP -------------------------------------------------------------------'''


def get_log(LOG_FORMAT='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
            LOG_NAME='',
            LOG_FILE_INFO='engine.log',
            LOG_FILE_ERROR='engine.err'):

    log = logging.getLogger(LOG_NAME)
    log_formatter = logging.Formatter(LOG_FORMAT)

    # comment this to suppress console output
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_formatter)
    log.addHandler(stream_handler)

    file_handler_info = logging.FileHandler(LOG_FILE_INFO, mode='w')
    file_handler_info.setFormatter(log_formatter)
    file_handler_info.setLevel(logging.INFO)
    log.addHandler(file_handler_info)

    file_handler_error = logging.FileHandler(LOG_FILE_ERROR, mode='w')
    file_handler_error.setFormatter(log_formatter)
    file_handler_error.setLevel(logging.ERROR)
    log.addHandler(file_handler_error)

    log.setLevel(logging.INFO)

    return log


def start_engine():

    # This function will be scheduled
    rt = engine.engine(datetime.now(), logger, lag, email)

    # Record the running time
    logging.info('Running time: ' + str(int(rt / 60)) + ' minute(s)\n')


if __name__ == '__main__':

    # Print some info
    print('SSC engine is running.\nLog file location: ' +
          str(os.path.dirname(os.path.abspath(__file__))) +
          '\nPID: ' + str(os.getpid()) +
          '\nYou can stop the Scheduler by pressing CTRL+Z...')

    # Logging setup
    logger = get_log()

    # Scheduler definiton
    sched = Scheduler()

    # Scheduler setup
    sched.add_cron_job(start_engine, minute=interval)

    # Scheduler start
    sched.start()
