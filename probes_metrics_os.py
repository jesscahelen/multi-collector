import psutil


class ProbesMetricOs:

    def __init__(self):
        # calcular em x segundos
        pass

    def get_total_memory(self):
        return psutil.virtual_memory()[0]

    def get_available_memory(self):
        return psutil.virtual_memory()[1]

    def get_memory_used_from_process(self, process_name):
        for proc in psutil.process_iter(['name', 'memory_percent']):
            if process_name in proc.info['name']:
                return proc.info

    def get_disk_space(self):
        return psutil.disk_usage('/')[2]

    def get_cpu_usage(self, interval):
        return psutil.cpu_percent(interval)

    def get_disk_write(self):
        return psutil.disk_io_counters()[1]

    def get_disk_reads(self):
        return psutil.disk_io_counters()[0]
