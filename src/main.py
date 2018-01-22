from subprocess import call
import time
import os

from apscheduler.schedulers.background import BackgroundScheduler


def job():
    #print("In job")
    call(['python3', 'update.py'])
    #call(['python', 'show.py'])


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(job, 'interval', seconds=45)
    scheduler.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(5)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()

