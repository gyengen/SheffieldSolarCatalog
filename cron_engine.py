from apscheduler.scheduler import Scheduler
from datetime import datetime
import engine.engine as e
import logging
import sys
import os


__author__ = ["Gyenge, Norbert"]
__email__  = ["n.g.gyenge@sheffield.ac.uk"]


def get_logger(LOG_FORMAT     = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
		       LOG_NAME       = '',
		       LOG_FILE_INFO  = 'engine.log',
		       LOG_FILE_ERROR = 'engine.err'):

    log           = logging.getLogger(LOG_NAME)
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
	rt = e.engine(datetime.now(), os.path.dirname(os.path.abspath(__file__)), logger)
	rt =1 
	# Record the running time
	logging.info('Running time: ' + str(int(rt/60)) + ' minute(s)\n')

if __name__ == '__main__':

	# Print some info
	print('SSC engine is running.\nLog file location: ' +
		  str(os.path.dirname(os.path.abspath(__file__))) +
		  '\nPID: ' + str(os.getpid()) +
		  '\nYou can stop the Scheduler by pressing CTRL+Z...')

	# Logging setup
	#logging.basicConfig(filename = 'cron.log', level = logging.INFO)
	#logger = logging.getLogger(__name__)
	logger = get_logger()

	# Scheduler definiton
	sched = Scheduler(standalone = True)

	# Scheduler setup
	sched.add_cron_job(start_engine, second = '0,15,30,45')

	# Scheduler start
	sched.start()
