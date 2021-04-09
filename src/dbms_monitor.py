import os
from decouple import config
import mysql.connector
import time
import csv
from datetime import datetime
from src.dbms_manager import *

class DBMSMonitor:
    """
    Monitor the global status of the DBMS.
    """

    def __init__(self, interval, total_time):
        self.interval = interval
        self.total_time = total_time
        self.cursor = DBMSManager.cursor
    
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(filename)s %(message)s',level=logging.DEBUG)

    def get_global_status(self):
        """
        Get the global status of the DBMS. Returns an array with the title of the columns
        and its rows.
        """
        has_titles = False
        counter = 0
        row_with_titles = []
        while (counter < self.total_time):
            self.cursor.execute('SHOW GLOBAL STATUS;')
            titles = []
            row = []
            if not has_titles:
                for c in self.cursor:
                    titles.append(c[0])
                    row.append(c[1])
                has_titles = True
            else:
                for c in self.cursor:
                    row.append(c[1])
            if len(titles) > 0:
                row_with_titles.append(titles)
            row_with_titles.append(row)
            time.sleep(self.interval)
            counter+=1
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
