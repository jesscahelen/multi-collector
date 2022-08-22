from dbms_manager import *
from bench_manager import *
from probes_metrics_os import *
from dbms_monitor import *
import logging
import threading
import time


class ExperimentalManager():

    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(filename)s %(message)s', level=logging.DEBUG)

    def __init__(self):
        self.dbms_manager = DBMSManager()
        self.bench_manager = BenchManager()
        self.probes_metrics_os = ProbesMetricOs()
        self.dbms_monitor = DBMSMonitor()
        DB_HOST = config('DB_HOST')
        DB_PORT = config('DB_PORT')
        DB_USER = config('DB_USER')
        DB_SECRET = config('DB_SECRET')

        try:
            self.connector = mysql.connector.connect(host=DB_HOST, port=DB_PORT,
                                                     user=DB_USER, password=DB_SECRET)
            self.cursor = self.connector.cursor()
        except mysql.connector.Error as err:
            logging.error("Something went wrong: ", err)

    def prepare(self):
        self.dbms_manager.update_config()
        self.dbms_manager.write_config()
        self.dbms_manager.config_db_for_benchmark()
        self.bench_manager.clean_up_schema()
        self.bench_manager.populate_schema()
        # self.bench_manager.cold_backup()

    def time_prepate(self):  # why does have a backup? i dont understand...
        # it is to not prepare the schema always?
        # it does not, because it prepares according to benchmark config file.
        # so, i will remove it for now.
        # self.bench_manager.restore_cold_backup()  # this should be preparation phase
        self.dbms_manager.restart_dbms()  # this should be preparation too

    def run(self):
        t1 = threading.Thread(target=self.bench_work)
        t2 = threading.Thread(target=self.get_metrics_work)
        t1.start()
        t2.start()

    def bench_work(self):
        self.bench_manager.run_benchmark()

    # the benchmark run several times, and the metrics too. that makes sense, but... i think it should be
    # coordinated, or at least have some error handling well done, because the benchmark could be down.
    def get_metrics_work(self):
        self.probes_metrics_os.write_metrics()
        self.dbms_monitor.write_metrics()
