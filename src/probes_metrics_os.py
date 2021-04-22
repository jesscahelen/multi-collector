import logging
import psutil
import time
import csv
from datetime import datetime
from decouple import config

class ProbesMetricOs:
    """
    Probes the OS metrics in an interval of time.
    """

    def __init__(self):
        self.RUN_INTERVAL = int(config('RUN_INTERVAL'))
        self.RUN_TOTAL_TIME =  int(config('RUN_TOTAL_TIME'))
        self.OS_PROCESS_NAME = config('OS_PROCESS_NAME')
    
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(filename)s %(message)s',level=logging.DEBUG)
    
    def run_metric_collections(self):
        """
        Get the metrics of OS and return an array of arrays of each interval of time.
        """
        counter = 0
        collection = []
        while(counter < self.RUN_TOTAL_TIME):
            now = str(datetime.now())
            row = []
            row.append(now)
            row.append(str(self.RUN_INTERVAL))
            row.append(str(self.get_total_memory()))
            row.append(str(self.get_available_memory()))
            row.append(str(self.OS_PROCESS_NAME))
            row.append(str(self.get_memory_used_from_process(self.OS_PROCESS_NAME)))
            row.append(str(self.get_available_disk_space()))
            row.append(str(self.get_cpu_usage(self.RUN_INTERVAL)))
            row.append(str(self.get_disk_write(self.RUN_INTERVAL)))
            row.append(str(self.get_disk_reads(self.RUN_INTERVAL)))
            counter+=1
            collection.append(row)
        return collection

    def get_total_memory(self):
        """
        Get the total amount of existent memory.
        """
        return psutil.virtual_memory()[0]

    def get_available_memory(self):
        """
        Get the total amount of available memory.
        """
        return psutil.virtual_memory()[1]
        
    def get_memory_used_from_process(self, process_name):
        """
        Get the percent of memory usage from a specific process.
        """
        for proc in psutil.process_iter(['name', 'memory_percent']):
            if process_name in proc.info['name']:
                return proc.info['memory_percent']

    def get_available_disk_space(self):
        """
        Get the total amount of available disk space.
        """
        return psutil.disk_usage('/')[2]

    def get_cpu_usage(self, interval):
        """
        Get the total percent of cpu usage.
        """
        return psutil.cpu_percent(interval)

    def get_disk_write(self, interval):
        """
        Get the amount of writes on disk in an interval of time.
        """
        p_before = psutil.disk_io_counters()[1]
        time.sleep(interval)
        p_after = psutil.disk_io_counters()[1]
        return p_after - p_before

    def get_disk_reads(self, interval):
        """
        Get the amount of reads on disk in an interval of time.
        """
        p_before = psutil.disk_io_counters()[0]
        time.sleep(interval)
        p_after = psutil.disk_io_counters()[0]
        return p_after - p_before

    def write_metrics(self):
        """
        Get the values of the metrics from run_metric_collections and write in a .csv file.
        """
        now = datetime.now()
        with open('os_collector' + str(now) + '.csv', mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['Datetime','Interval','Total Memory','Available Memory',
            'Process','Memory used from process','Disk space','CPU Usage','Disk Write','Disk Read'])
            for row in self.run_metric_collections():
                csv_writer.writerow(row)
        logging.info('OS Metric writen.')
            