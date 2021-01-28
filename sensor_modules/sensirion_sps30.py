"""
This module is for the Sensirion SPS30 USB
It Retrieves & Returns Sensor data to be written to the DB

Particulate Matter Sensor Specifications
Mass concentration accuracy
±10 μg/m3 @ 0 to 100 μg/m3
±10 % @ 100 to 1000 μg/m3

Mass concentration range: 1 to 1000 μg/m3
Mass concentration resolution: 1 μg/m3

Particle detection size range
Mass concentration: PM1.0, PM2.5, PM4 and PM10
Number concentration: PM0.5, PM1.0, PM2.5, PM4 and PM10

Lower limit of detection: 0.3 μm
Minimum sampling interval: 1 sec (continuous mode)
Lifetime: > 8 years operating continuously 24h/day
Dimensions: 40.6 x 40.6 x 12.2 mm3
Operating temperature range: -10 to +60 °C
Storage temperature range: -40 to +70 °C
Electrical Specifications
Interface: UART, I2C
Supply voltage: 4.5 – 5.5 V
Average supply current
@ 1 Hz measurement rate	< 60 mA

1 Specified for PM2.5 at 25 °C using potassium chloride salt particles and the
   TSI DustTrakTM DRX Aerosol Monitor 8533 as a reference.
2 PMx defines particles with a size smaller than "x" micrometers
   (e.g., PM2.5 = particles smaller than 2.5 μm).

Created on Tue May 18th 14:48:56 2020

@author: OO-Dragon
"""
import time
from threading import Thread
from operations_modules import logger
from configuration_modules import app_config_access

round_decimal_to = 5
# Update readings in seconds
sleep_between_readings_seconds = 1
max_readings_missed_before_driver_reset = 10

# Specify serial port name for sensor
# i.e. "COM10" for Windows or "/dev/ttyUSB0" for Linux
device_port = "/dev/ttyUSB0"


class CreateSPS30:
    """ Creates Function access to the Sensirion SPS30. """

    def __init__(self):
        self.pm1_var = 0.0
        self.pm25_var = 0.0
        self.pm4_var = 0.0
        self.pm10_var = 0.0

        self.readings_missed = 0

        try:
            self.sps30_pm_import = __import__("sensor_modules.drivers.SPS30.sps30", fromlist=["SPS30"])
            self.sensirion_sps30_access = self.sps30_pm_import.SPS30(device_port)
            self.sensirion_sps30_access.start()
            time.sleep(2)
            self.thread_readings_updater = Thread(target=self._readings_updater)
            self.thread_readings_updater.daemon = True
            self.thread_readings_updater.start()
            self.sensor_watchdog = Thread(target=self._sensor_watchdog)
            self.sensor_watchdog.daemon = True
            self.sensor_watchdog.start()
            logger.sensors_logger.debug("Sensirion SPS30 Initialization - OK")
        except Exception as error:
            logger.sensors_logger.error("Sensirion SPS30 Initialization - Failed: " + str(error))
            app_config_access.installed_sensors.sensirion_sps30 = 0
            app_config_access.installed_sensors.update_configuration_settings_list()

    def particulate_matter_data(self):
        """ Returns 3 Particulate Matter readings pm1, pm25, pm4 and pm10 as a list. """
        return [self.pm1_var, self.pm25_var, self.pm4_var, self.pm10_var]

    def _readings_updater(self):
        while True:
            try:
                logger.sensors_logger.debug("Sensirion SPS30 - Pre Get Data")
                pm_data = self.sensirion_sps30_access.read_values()
                logger.sensors_logger.debug("Sensirion SPS30 - Post Get Data")
                self.pm1_var = round(float(pm_data[0]), round_decimal_to)
                self.pm25_var = round(float(pm_data[1]), round_decimal_to)
                self.pm4_var = round(float(pm_data[2]), round_decimal_to)
                self.pm10_var = round(float(pm_data[3]), round_decimal_to)
                # Reset missed readings after reading update
                self.readings_missed = 0
            except Exception as error:
                logger.sensors_logger.warning("Sensirion SPS30 - Update readings Failed: " + str(error))
            time.sleep(sleep_between_readings_seconds)

    def _sensor_watchdog(self):
        while True:
            if self.readings_missed > max_readings_missed_before_driver_reset:
                self.pm1_var = 0.0
                self.pm25_var = 0.0
                self.pm4_var = 0.0
                self.pm10_var = 0.0

                self.sensirion_sps30_access.stop()
                self.sensirion_sps30_access.close_port()
                time.sleep(0.5)
                self.sensirion_sps30_access.__init__(device_port)
                time.sleep(1)
                self.sensirion_sps30_access.start()
            time.sleep(sleep_between_readings_seconds)
            self.readings_missed += 1
