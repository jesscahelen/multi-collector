import os
import logging
from decouple import config
import mysql.connector
import time
import csv
from datetime import datetime
from decouple import config
from dbms_manager import *

class DBMSMonitor:
    """
    Monitor the global status of the DBMS.
    """

    def __init__(self):
        self.RUN_INTERVAL = int(config('RUN_INTERVAL'))
        self.RUN_TOTAL_TIME =  int(config('RUN_TOTAL_TIME'))
        self.dbms_manager = DBMSManager()
    
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(filename)s %(message)s',level=logging.DEBUG)

    def get_global_status(self):
        """
        Get the global status of the DBMS. Returns an array with the title of the columns
        and its rows.
        """
        has_titles = False
        counter = 0
        row_with_titles = []
        while (counter < self.RUN_TOTAL_TIME):
            if self.dbms_manager.connector.is_connected():
                self.dbms_manager.cursor.execute('SHOW GLOBAL STATUS;')
                titles = []
                row = []
                if not has_titles:
                    for c in self.dbms_manager.cursor:
                        titles.append(c[0])
                        row.append(c[1])
                    has_titles = True
                else:
                    for c in self.dbms_manager.cursor:
                        row.append(c[1])
                if len(titles) > 0:
                    row_with_titles.append(titles)
                row_with_titles.append(row)
                time.sleep(self.RUN_INTERVAL)
                counter+=1
            else:
                logging.error('DBMS is not up. Check the DBMS Manager error log.')
                self.dbms_manager.get_error_from_container()
        return row_with_titles

    def write_metrics(self):
        """
        Get the global status from the get_global_status method and write in a .csv file.
        """
        now = datetime.now()
        with open('dbms_collector_global_status' + str(now) + '.csv', mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            for row in self.get_global_status():
                csv_writer.writerow(row)
        logging.info('Global status writen.')
