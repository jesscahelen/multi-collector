import os
import logging
from decouple import config
import mysql.connector
import time
import csv
from datetime import datetime

class DBMSManager:

    def __init__(self):
        pass
    
    DB_HOST=config('DB_HOST')
    DB_PORT=config('DB_PORT')
    DB_USER=config('DB_USER')
    DB_SECRET=config('DB_SECRET')
    
    try:
        connector = mysql.connector.connect(host=DB_HOST, port=DB_PORT, 
        user=DB_USER, password=DB_SECRET)
        cursor = connector.cursor()
    except mysql.connector.Error as err:
        logging.error("Something went wrong: ", err)
    

    def read_config(self):
        row_with_titles = []
        self.cursor.execute('SELECT * FROM performance_schema.global_variables;')
        titles = []
        row = []
        for c in self.cursor:
            titles.append(c[0])
            row.append(c[1])
        row_with_titles.append(titles)
        row_with_titles.append(row)
        return row_with_titles

    def write_config(self):
        now = datetime.now()
        with open('dbms_collector_global_variables' + str(now) + '.csv', mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            for row in self.read_config():
                csv_writer.writerow(row)
        logging.info('Global variables writen.')
    
    def update_config(self):
        with open('db_config_input.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                    continue
                else:
                    query = 'SET PERSIST %s = %s;' % (row[1], row[2])
                    logging.info('Query:' + query)
                    try:
                        self.cursor.execute(query)
                    except mysql.connector.DatabaseError as err:
                        logging.error("Something went wrong: ", err)
                    line_count += 1
        logging.info(f'Processed {line_count} lines.')

    def restart_dbms(self):
        try:
            self.cursor.execute('RESTART')
        except mysql.connector.Error as err:
            logging.error("Something went wrong: ", err)
        print('Restarting DBMS...')
        