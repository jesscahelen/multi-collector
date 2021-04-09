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

    def __init__(self):
        pass

    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(filename)s %(message)s',level=logging.DEBUG)
    
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
        """
        Read current config from database using a query from performance_schema.global_variables.
        Returns an array of titles of colunms and its rows.
        """
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
    
    def config_db_for_benchmark(self):
        """
        Create a specific user and database for benchmark usage.
        """
        try:
            self.cursor.execute("CREATE USER IF NOT EXISTS 'oltpbench'@'%' IDENTIFIED BY 'Oltpbench123!';")
            self.cursor.execute('CREATE DATABASE tpcc;')
            self.cursor.execute("GRANT ALL PRIVILEGES ON tpcc.* TO 'oltpbench'@'%';")
        except Error as err:
            logging.error("Something went wrong: ", err)

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
    
    def update_config(self, cnf_file_location, container):
        """
        Read the db_config_input.csv file and update the configurations
        of the .cnf file of DBMS with these values.
        And then, restart the DBMS to get the updated configurations.
        If some configuration affects the docker container health, a log 
        file will be created with the error log from the container.
        """
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
        self.restart_dbms(container)
        time.sleep(5)
        if not self.check_if_container_is_running(container):
            error_file = self.get_error_from_container(container)
            logging.error("Something went wrong updating the configurations. The error log will be collected on: " + error_file)

    def restart_dbms(self, container):
        """
        Restart a container.
        """
        try:
            bash_cmd = ["docker", "restart", container]
            process = subprocess.run(bash_cmd, capture_output=True, text=True)
            output = process.sterr
        except Error as err:
            logging.error(output + "\n" + "Something went wrong: ", err)
        logging.info('Restarting DBMS...')

    def stop_dbms(self, container):
        """
        Stop a container.
        """
        try:
            bash_cmd = ["docker", "stop", container]
            process = subprocess.run(bash_cmd, capture_output=True, text=True)
            output = process.sterr
        except Error as err:
            logging.error(output + "\n" + "Something went wrong: ", err)
        logging.info('Container ' + container + ' stopped.')
    
    def start_dbms(self, container):
        """
        Start a container.
        """
        try:
            bash_cmd = ["docker", "start", container]
            process = subprocess.run(bash_cmd, capture_output=True, text=True)
            output = process.sterr
        except Error as err:
            logging.error(output + "\n" + "Something went wrong: ", err)
        logging.info('Container ' + container + ' started.')
        
    def get_error_from_container(self, container):
        """
        Get error log from a container. Returns the log file name.
        """
        bash_cmd = ["docker", "logs", container]
        process = subprocess.run(bash_cmd, capture_output=True, text=True)
        output = process.stderr
        return self.write_log(output)
        
    def check_if_container_is_running(self, container):
        """
        Call the command 'docker ps' to check if the container is up.
        Returns True if the container is up and False if it's down.
        """
        bash_cmd = ["docker", "ps"]
        print(bash_cmd)
        process = subprocess.run(bash_cmd, capture_output=True, text=True)
        output = process.stdout
        if output in container:
            logging.info('The container' + container + ' is up.')
            return True
        logging.info('The container' + container + ' is down.')
        return False
    
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