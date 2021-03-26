import mysql.connector
import time
import csv
from datetime import datetime

class DBMSMonitor:

    #TODO: make env variables for db
    connector = mysql.connector.connect(user='root', port='3306', password='senha')
    cursor = connector.cursor()

    def __init__(self, interval, total_time):
        self.interval = interval
        self.total_time = total_time

    def get_global_status(self):
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
            print('adicionou uma linha :)')
            time.sleep(self.interval)
            counter+=1
        return row_with_titles

    def write_metrics(self):
        now = datetime.now()
        with open('dbms_collector' + str(now) + '.csv', mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            for row in self.get_global_status():
                csv_writer.writerow(row)

