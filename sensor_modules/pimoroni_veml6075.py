"""
This module is for the Pimoroni VEML6075
It Retrieves & Returns Sensor data to be written to the DB

VEML6075 UVA/B sensor
Detects raw UVA/UVB and UVA/UVB and average indices
3.3V or 5V compatible
I2C interface (address 0x10)
Reverse polarity protection
Raspberry Pi-compatible pinout (pins 1, 3, 5, 7, 9)

pip3 install veml6075

Created on Tue June 25 10:53:56 2019

@author: OO-Dragon
"""
from operations_modules import logger
from operations_modules import app_config_access

round_decimal_to = 5


class CreateVEML6075:
    """ Creates Function access to the Pimoroni VEML6075. """

    def __init__(self):
        try:
            self.veml6075_import = __import__('veml6075')
            self.smbus_import = __import__('smbus')
            self.bus = self.smbus_import.SMBus(1)
            self.uv_sensor = self.veml6075_import.VEML6075(i2c_dev=self.bus)
            self.uv_sensor.set_shutdown(False)
            self.uv_sensor.set_high_dynamic_range(False)
            self.uv_sensor.set_integration_time('100ms')
            logger.sensors_logger.debug("Pimoroni VEML6075 Initialization - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni VEML6075 Initialization - Failed: " + str(error))
            app_config_access.installed_sensors.pimoroni_veml6075 = 0

    def ultra_violet_index(self):
        """ Returns Ultra Violet Index. """
        try:
            uva, uvb = self.uv_sensor.get_measurements()
            uv_comp1, uv_comp2 = self.uv_sensor.get_comparitor_readings()
            uv_index = self.uv_sensor.convert_to_index(uva, uvb, uv_comp1, uv_comp2)
        except Exception as error:
            uv_index = [0.0, 0.0, 0.0]
            logger.sensors_logger.error("Pimoroni VEML6075 UV Index Reading - Failed: " + str(error))

        return uv_index[2]

    def ultra_violet(self):
        """ Returns Ultra Violet (A,B) as a list. """
        try:
            uva, uvb = self.uv_sensor.get_measurements()
        except Exception as error:
            uva, uvb = [0.0, 0.0]
            logger.sensors_logger.error("Pimoroni VEML6075 UVA & UVB Readings - Failed: " + str(error))

        return_list_uva_uvb = [round(float(uva), round_decimal_to), round(float(uvb), round_decimal_to)]

        return return_list_uva_uvb

    def ultra_violet_comparator(self):
        """ Returns 2 Ultra Violet comparator as a list. """
        try:
            uv_comp1, uv_comp2 = self.uv_sensor.get_comparitor_readings()
        except Exception as error:
            uv_comp1, uv_comp2 = [0.0, 0.0]
            logger.sensors_logger.error("Pimoroni VEML6075 UVA & UVB Readings - Failed: " + str(error))

        return_list_uv_comparator = [round(float(uv_comp1), round_decimal_to), round(float(uv_comp2), round_decimal_to)]

        return return_list_uv_comparator
