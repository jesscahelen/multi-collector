import os
import subprocess
import configparser
import logging
from decouple import config
import mysql.connector
import time
import csv
from datetime import datetime


class DBMSManager:
    """
    Manage actions of DBMS.
    """

    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(filename)s %(message)s', level=logging.DEBUG)

    def __init__(self):
        self.DB_CONTAINER_NAME = config('DB_CONTAINER_NAME')
        self.RUN_INTERVAL = int(config('RUN_INTERVAL'))
        self.DB_HOST = config('DB_HOST')
        self.DB_PORT = config('DB_PORT')
        self.DB_USER = config('DB_USER')
        self.DB_SECRET = config('DB_SECRET')
        self.connector = None

        try:
            self.connector = mysql.connector.connect(host=self.DB_HOST, port=self.DB_PORT,
                                                     user=self.DB_USER, password=self.DB_SECRET)
            self.cursor = self.connector.cursor()
            self.cursor.execute('set max_allowed_packet=67108864')
        except mysql.connector.Error as err:
            logging.error("Something went wrong: ", err)

    def read_config(self):
        """
        Read current config from database using a query from performance_schema.global_variables.
        Returns an array of titles of colunms and its rows.
        """
        row_with_titles = []
        while not self.connector.is_connected():
            logging.error("DBMS not available. Trying to reconnect...")
            self.connector.ping(reconnect=True, attempts=2, delay=5)
        if self.connector.is_connected():
            self.cursor.execute('USE performance_schema;')
            self.cursor.execute(
                'SELECT * FROM performance_schema.global_variables;')
            titles = []
            row = []
            for c in self.cursor:
                titles.append(c[0])
                row.append(c[1])
            row_with_titles.append(titles)
            row_with_titles.append(row)
        return row_with_titles

    def config_db_for_benchmark(self):
        """
        Create a specific user and database for benchmark usage.
        """
        while not self.connector.is_connected() or not self.connector.ping():
            logging.error("DBMS not available. Trying to reconnect...")
            self.connector.ping(reconnect=True, attempts=2, delay=5)
        if self.connector.ping():
            self.cursor.execute(
                "CREATE USER IF NOT EXISTS 'oltpbench'@'%' IDENTIFIED BY 'Oltpbench123!';")
            self.cursor.execute('CREATE DATABASE IF NOT EXISTS tpcc;')
            self.cursor.execute(
                "GRANT ALL PRIVILEGES ON tpcc.* TO 'oltpbench'@'%';")
        else:
            print("deu ruim no banco :(")

    def write_config(self):
        """
        Write the current config into a .csv file, getting the config through read_config method.
        """
        now = datetime.now()
        with open('dbms_collector_global_variables' + str(now) + '.csv', mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            for row in self.read_config():
                csv_writer.writerow(row)
        logging.info('Global variables writen.')

    def update_config(self):
        """
        Read the db_config_input.csv file and update the configurations
        of the .cnf file of DBMS with these values.
        And then, restart the DBMS to get the updated configurations.
        If some configuration affects the docker container health, a log 
        file will be created with the error log from the container.
        """
        cnf_file_location = config('DB_CONF_PATH')
        config_dict = configparser.ConfigParser()
        config_dict['mysqld'] = {}
        with open('db_config_input.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                    continue
                else:
                    config_dict['mysqld'][row[1]] = row[2]
                    logging.info(f'Config Added: {row[1]}={row[2]}')
                    line_count += 1
        with open(cnf_file_location, 'w') as config_file:
            config_dict.write(config_file)
        logging.info(f'Processed {line_count} lines.')
        self.restart_dbms()

    def restart_dbms(self):
        """
        Restart a container.
        """
        logging.info('restart_dbms Started')
        try:
            bash_cmd = ["docker", "restart", self.DB_CONTAINER_NAME]
            process = subprocess.run(bash_cmd, capture_output=True, text=True)
            output = process.stderr
        except Error as err:
            logging.error(output + "\n" + "Something went wrong: ", err)
        try:
            self.connector.ping(reconnect=True, attempts=2, delay=5)
        except mysql.connector.Error as err:
            logging.error("Something went wrong: ", err)
        logging.info('Restarting DBMS...')

    def stop_dbms(self):
        """
        Stop a container.
        """
        try:
            bash_cmd = ["docker", "stop", self.DB_CONTAINER_NAME]
            process = subprocess.run(bash_cmd, capture_output=True, text=True)
            output = process.stderr
        except Error as err:
            logging.error(
                output + "\n" + "Something went wrong when stopping the container" + container + ": ", err)
        logging.info('Container ' + self.DB_CONTAINER_NAME + ' stopped.')

    def get_error_from_container(self):
        """
        Get error log from a container. Returns the log file name.
        """
        bash_cmd = ["docker", "logs", self.DB_CONTAINER_NAME]
        process = subprocess.run(bash_cmd, capture_output=True, text=True)
        output = process.stderr
        return self.write_log(output)

    def write_log(self, log):
        """
        Get the log from a container and write in a .log file.
        Returns the file name.
        """
        now = datetime.now()
        file_name = 'dbms_manager_error' + str(now) + '.log'
        with open(file_name, mode='w') as log_file:
            log_file.write(log)
        logging.info('Log file writen.')
        return file_name
