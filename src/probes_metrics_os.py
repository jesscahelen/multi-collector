import psutil
import time
import csv
from datetime import datetime

class ProbesMetricOs:

    def __init__(self, interval, total_time, process_name):
        self.interval = interval
        self.total_time = total_time
        self.process_name = process_name
    
    def run_metric_collections(self):
        counter = 0
        collection = []
        while(counter < self.total_time):
            now = str(datetime.now())
            row = []
            row.append(now)
            row.append(str(self.interval))
            row.append(str(self.get_total_memory()))
            row.append(str(self.get_available_memory()))
            row.append(str(self.process_name))
            row.append(str(self.get_memory_used_from_process(self.process_name)))
            row.append(str(self.get_disk_space()))
            row.append(str(self.get_cpu_usage(self.interval)))
            row.append(str(self.get_disk_write(self.interval)))
            row.append(str(self.get_disk_reads(self.interval)))
            counter+=1
            collection.append(row)
        return collection

    def get_total_memory(self):
        return psutil.virtual_memory()[0]

    def get_available_memory(self):
        return psutil.virtual_memory()[1]

    def get_memory_used_from_process(self, process_name):
        for proc in psutil.process_iter(['name', 'memory_percent']):
            if process_name in proc.info['name']:
                return proc.info['memory_percent']

    def get_disk_space(self):
        return psutil.disk_usage('/')[2]

    def get_cpu_usage(self, interval):
        return psutil.cpu_percent(interval)

    def get_disk_write(self, interval):
        p_before = psutil.disk_io_counters()[1]
        time.sleep(interval)
        p_after = psutil.disk_io_counters()[1]
        return p_after - p_before

    def get_disk_reads(self, interval):
        p_before = psutil.disk_io_counters()[0]
        time.sleep(interval)
        p_after = psutil.disk_io_counters()[0]
        return p_after - p_before

    def write_metrics(self):
        now = datetime.now()
        with open('os_collector' + str(now) + '.csv', mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['Datetime','Interval','Total Memory','Available Memory',
            'Process','Memory used from process','Disk space','CPU Usage','Disk Write','Disk Read'])
            for row in self.run_metric_collections():
                csv_writer.writerow(row)
            