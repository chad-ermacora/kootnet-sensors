"""
This module is for the Pimoroni PMS5003
It Retrieves & Returns Sensor data to be written to the DB

Plantower PMS5003 Particulate Matter (PM) Sensor
Detects PM1, PM2.5, PM10 particulates
15cm Picoblade cable
UART serial interface
Dimensions: 50x38x21mm

pip install pms5003

Created on Tue June 25 10:53:56 2019

@author: OO-Dragon
"""
import os
import time
from threading import Thread
from operations_modules import logger
from configuration_modules import app_config_access
from operations_modules import app_generic_functions

round_decimal_to = 5
# Update readings in seconds
sleep_between_readings_seconds = 1


class CreatePimoroniPMS5003:
    """ Creates Function access to the Pimoroni PMS5003. """

    def __init__(self):
        if app_config_access.installed_sensors.pimoroni_pms5003:
            self.pm1_var = 0.0
            self.pm25_var = 0.0
            self.pm10_var = 0.0
            self.sensor_latency = 0.0

            try:
                pms5003_import = __import__("sensor_modules.drivers.pms5003", fromlist=["PMS5003"])
                self._enable_psm5003_serial()
                self.enviro_plus_pm_access = pms5003_import.PMS5003()
                self.thread_readings_updater = Thread(target=self._readings_updater)
                self.thread_readings_updater.daemon = True
                self.thread_readings_updater.start()
                logger.sensors_logger.debug("Pimoroni PMS5003 Initialization - OK")
            except Exception as error:
                logger.sensors_logger.error("Pimoroni PMS5003 Initialization - Failed: " + str(error))
                app_config_access.installed_sensors.pimoroni_pms5003 = 0
                app_config_access.installed_sensors.update_configuration_settings_list()

    def _readings_updater(self):
        logger.sensors_logger.debug("Pimoroni PMS5003 readings updater started")
        while True:
            try:
                start_time = time.time()
                enviro_plus_pm_data = self.enviro_plus_pm_access.read()
                end_time = time.time()
                self.sensor_latency = float(end_time - start_time)
                self.pm1_var = enviro_plus_pm_data.pm_ug_per_m3(1.0)
                self.pm25_var = enviro_plus_pm_data.pm_ug_per_m3(2.5)
                self.pm10_var = enviro_plus_pm_data.pm_ug_per_m3(10)
            except Exception as error:
                logger.sensors_logger.error("Pimoroni PMS5003 Readings Update Failed: " + str(error))
                self.pm1_var = 0.0
                self.pm25_var = 0.0
                self.pm10_var = 0.0
            time.sleep(sleep_between_readings_seconds)

    def particulate_matter_data(self):
        """ Returns 3 Particulate Matter readings PM1, PM25 and PM10 in a list as floats. """
        return [round(self.pm1_var, round_decimal_to),
                round(self.pm25_var, round_decimal_to),
                round(self.pm10_var, round_decimal_to)]

    @staticmethod
    def _enable_psm5003_serial():
        logger.sensors_logger.debug("Enabling Serial for Pimoroni PSM5003")
        try:
            serial_disabled = True
            boot_config_lines = app_generic_functions.get_file_content("/boot/config.txt").split("\n")

            new_config = ""
            for line in boot_config_lines:
                if line.strip() == "dtoverlay=pi3-miniuart-bt":
                    serial_disabled = False
                new_config += line + "\n"

            if serial_disabled:
                logger.sensors_logger.info("Serial not enabled for PSM5003 - Enabling")
                logger.primary_logger.warning("You must reboot the System before the PSM5003 will function properly")
                os.system("raspi-config nonint set_config_var enable_uart 1 /boot/config.txt")
                os.system("raspi-config nonint do_serial 1")
                time.sleep(0.5)
                new_config = new_config.strip()
                new_config += "\n\n# Kootnet Sensors Addition\ndtoverlay=pi3-miniuart-bt\n"
                app_generic_functions.write_file_to_disk("/boot/config.txt", new_config)
        except Exception as error:
            logger.sensors_logger.error("Pimoroni PSM5003 Enable Serial - Failed: " + str(error))
