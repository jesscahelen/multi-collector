from configparser import Error
from dbms_manager import *
import subprocess
from decouple import config
import logging


class BenchManager:

    def __init__(self):
        self.dbms_manager = DBMSManager()
        self.BENCH_CONFIG_PATH = config('BENCH_CONFIG_PATH')
        self.BENCH_RESULT_PATH = config('BENCH_RESULT_PATH')
        self.DB_CONTAINER_NAME = config('DB_CONTAINER_NAME')
        self.DB_DATA_PATH = config('DB_DATA_PATH')
        self.DB_BACKUP_PATH = config('DB_BACKUP_PATH')
        self.RUN_INTERVAL = config('RUN_INTERVAL')
        self.RUN_TOTAL_TIME = config('RUN_TOTAL_TIME')

    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(filename)s %(message)s', level=logging.DEBUG)

    def clean_up_schema(self):
        try:
            if self.dbms_manager.connector.is_connected():
                self.dbms_manager.cursor.execute("DROP SCHEMA IF EXISTS tpcc;")
                self.dbms_manager.cursor.execute("CREATE SCHEMA tpcc;")
        except Error as err:
            logging.error(
                "Something went wrong when call clean_up_schema(): ", err)

#check_call
    def populate_schema(self):
        bash_cmd = ["cat", self.BENCH_CONFIG_PATH, "|", "sudo", "docker", "run", "-i", "--rm", "--name=oltpbench", "--network=multi-collector_oltpbench",
                    "oltpbench", "-b", "tpcc", "--create=true", "--load=true"]
        #cat ./benchmark/config/mysql_tpcc_config.xml | docker run -i --rm --name=oltpbench --network=multi-collector_oltpbench oltpbench -b tpcc --create=true --load=true
        try:
            process = subprocess.run(bash_cmd, shell=True, capture_output=True)
            print(process)
            output = process.stderr
        except Error as err:
            logging.error(
                output + "\n" + "Something went wrong when call populate_schema(): ", err)
        logging.info('Schema tpcc populated.')

    def cold_backup(self):
        rm_backup = ["rm", "-rf", self.DB_BACKUP_PATH]
        cp_backup = ["cp", "-a", self.DB_DATA_PATH + "/*", self.DB_BACKUP_PATH]
        self.dbms_manager.stop_dbms()
        try:
            process = subprocess.run(rm_backup, capture_output=True, text=True)
            output = process.stderr
        except Error as err:
            logging.error(
                output + "\n" + "Something went wrong when removing the DBMS backup folder: ", err)
        try:
            process = subprocess.run(cp_backup, capture_output=True, text=True)
            output = process.stderr
        except Error as err:
            logging.error(
                output + "\n" + "Something went wrong when doing the cold backup: ", err)
        logging.info('Cold Backup done.')

    def restore_cold_backup(self):
        logging.info('restore_cold_backup Started')
        rm_backup = ["rm", "-rf", self.DB_DATA_PATH]
        cp_backup = ["cp", "-a", self.DB_BACKUP_PATH + "/*", self.DB_DATA_PATH]
        self.dbms_manager.stop_dbms()
        try:
            process = subprocess.run(rm_backup, capture_output=True, text=True)
            output = process.stderr
        except Error as err:
            logging.error(
                output + "\n" + "Something went wrong when removing the DBMS backup folder: ", err)
        try:
            process = subprocess.run(cp_backup, capture_output=True, text=True)
            output = process.stderr
        except Error as err:
            logging.error(
                output + "\n" + "Something went wrong when restorring the cold backup: ", err)
        logging.info('Restore of backup done.')

    def run_benchmark(self):
        logging.info('run_benchmark Started')
        count = 0
        volume = str(self.BENCH_RESULT_PATH) + ":/usr/src/oltpbench/results"
        bash_cmd = ["cat", self.BENCH_CONFIG_PATH, "|", "docker", "run", "-i",
                    "--rm", "--name=oltpbench", "--network=oltpbench", "-v", volume,
                    "oltpbench", "-b", "tpcc", "--execute=true", "-o", "result"]
        try:
            process = subprocess.run(
                bash_cmd, capture_output=True, text=True)
            output = process.stderr
        except Error as err:
            logging.error(
                output + "\n" + "Something went wrong when running run_benchmark(): ", err)
        logging.info('Benchmark ran each ' + self.RUN_INTERVAL +
                     ' seconds, ' + self.RUN_TOTAL_TIME + ' times.')
#cat ./benchmark/config/mysql_tpcc_config.xml | sudo docker run -i --rm --name=oltpbench -v /home/jessica/tg/multi-collector/benchmark/result:/usr/src/oltpbench/results oltpbench -b tpcc --execute=true -s 2 -o result