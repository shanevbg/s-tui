import os
import time

from Source import Source

class RaplPowerSource(Source):

    intel_rapl_folder = '/sys/class/powercap/intel-rapl/'

    MICRO_JAUL_IN_JAUL = 1000000.0

    def __init__(self, package_number = 0):
        self.package_number = package_number
        self.intel_rapl_package_energy_file = os.path.join(self.intel_rapl_folder, 'intel-rapl:%d'%package_number, 'energy_uj')
        self.intel_rapl_package_max_energy_file = os.path.join(self.intel_rapl_folder, 'intel-rapl:%d'%package_number, 'constraint_0_max_power_uw')
        if (not os.path.exists(self.intel_rapl_package_energy_file) or not os.path.exists(self.intel_rapl_package_max_energy_file)):
            self.is_available = False
            self.last_measurement_time = 0
            self.last_measurement_value = 0
            self.max_power = 0
            self.last_wats = 0
            return

        self.is_available = True
        self.last_measurement_time = time.time()
        self.last_measurement_value = self.read_power_measurement_file()
        self.max_power = self.read_max_power_file() / self.MICRO_JAUL_IN_JAUL
        self.last_wats = 0

    def read_measurement(self, file_path):
        file = open(file_path)
        value = file.read()
        file.close()
        return float(value)

    def read_max_power_file(self):
        if not self.is_available:
            return -1
        return float(self.read_measurement(self.intel_rapl_package_max_energy_file))

    def read_power_measurement_file(self):
        if not self.is_available:
            return -1
        return float(self.read_measurement(self.intel_rapl_package_energy_file))

    def get_power_usage(self):
        if not self.is_available:
            return -1
        current_measurement_value = self.read_power_measurement_file()
        current_measurement_time = time.time()

        jaul_used = (current_measurement_value - self.last_measurement_value) / self.MICRO_JAUL_IN_JAUL
        seconds_passed = current_measurement_time - self.last_measurement_time
        wats_used = jaul_used / seconds_passed

        self.last_measurement_value = current_measurement_value
        self.last_measurement_time = current_measurement_time
        self.last_wats = wats_used
        return wats_used

    # Source super class implementation
    def get_is_available(self):
        return self.is_available

    def get_reading(self):
        return self.get_power_usage()

    def get_maximum(self):
        return self.max_power

    def get_summary(self):
        return {'Cur Power': '%d %s' % (self.last_wats, self.get_measurement_unit())
                , 'Max Power': '%d %s' % (self.max_power, self.get_measurement_unit())}

    def get_source_name(self):
        return 'Rapl Power'

    def get_measurement_unit(self):
        return 'W'


if '__main__' == __name__:
    rapl = RaplPower()
    while True:
        print(rapl.get_power_usage())
        time.sleep(2)
