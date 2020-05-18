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

1 Specified for PM2.5 at 25 °C using potassium chloride salt particles and the TSI DustTrakTM DRX Aerosol Monitor 8533 as a reference.
2 PMx defines particles with a size smaller than "x" micrometers (e.g., PM2.5 = particles smaller than 2.5 μm).

Created on Tue May 18th 14:48:56 2020

@author: OO-Dragon
"""
import time
from operations_modules import logger
from operations_modules import app_config_access

round_decimal_to = 5
pause_sensor_during_access_sec_pm = 0.02

# Specify serial port name for sensor
# i.e. "COM10" for Windows or "/dev/ttyUSB0" for Linux
device_port = "/dev/ttyUSB0"


class CreateSPS30:
    """ Creates Function access to the Sensirion SPS30. """

    def __init__(self):
        self.sensor_in_use = False
        try:
            sps30_pm_import = __import__("sensor_modules.drivers.SPS30.sps30", fromlist=["SPS30"])
            self.sensirion_sps30_access = sps30_pm_import.PMS5003()
            self.sensirion_sps30_access.start()
            logger.sensors_logger.debug("Sensirion SPS30 Initialization - OK")
        except Exception as error:
            logger.sensors_logger.error("Sensirion SPS30 Initialization - Failed: " + str(error))
            app_config_access.installed_sensors.sensirion_sps30 = 0

    def particulate_matter_data(self):
        """ Returns 3 Particulate Matter readings pm1, pm25 and pm10 as a list. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec_pm)
        self.sensor_in_use = True
        try:
            pm_data = self.sensirion_sps30_access.read_values()
            pm1 = pm_data[0]
            pm25 = pm_data[1]
            pm10 = pm_data[3]
        except Exception as error:
            logger.sensors_logger.error("Sensirion SPS30 Particulate Matter Update - Failed: " + str(error))
            pm1 = 0.0
            pm25 = 0.0
            pm10 = 0.0
        self.sensor_in_use = False
        return [round(pm1, round_decimal_to),
                round(pm25, round_decimal_to),
                round(pm10, round_decimal_to)]
