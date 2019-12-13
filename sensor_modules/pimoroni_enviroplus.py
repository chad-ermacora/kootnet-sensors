"""
This module is for the Pimoroni Enviro+
It Retrieves & Returns Sensor data to be written to the DB

BME280 temperature, pressure, humidity sensor
LTR-559 light and proximity sensor
MICS6814 analog gas sensor
ADS1015 analog to digital converter (ADC)
MEMS microphone
0.96" colour LCD (160x80)
Connector for particulate matter (PM) sensor*

pip install enviroplus

Created on Tue June 25 10:53:56 2019

@author: OO-Dragon
"""
import os
import time
from threading import Thread
from operations_modules import logger
from operations_modules import app_config_access
from operations_modules import file_locations
from operations_modules import app_generic_functions
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

round_decimal_to = 5
turn_off_display_seconds = 25
readings_update_threshold_sec = 0.25
pause_sensor_during_access_sec = 0.02
pause_sensor_during_access_sec_gas = 0.095
pause_sensor_during_access_sec_pm = 0.002


class CreateEnviroPlus:
    """ Creates Function access to the Pimoroni Enviro+. """
    def __init__(self):
        try:
            self.display_off_count = 0
            self.display_is_on = True

            self.display_in_use = False
            self.sensor_in_use = False

            self.pm_readings_last_updated = time.time()
            self.pm1 = 0.0
            self.pm25 = 0.0
            self.pm10 = 0.0

            self.font = ImageFont.truetype(file_locations.display_font, 40)

            ltr559_import = __import__("sensor_modules.drivers.ltr559", fromlist=["LTR559"])
            bme280_import = __import__("sensor_modules.drivers.enviroplus.custom-bme280", fromlist="BME280")
            self.gas_access = __import__("sensor_modules.drivers.enviroplus.mics6814", fromlist=["read_all"])
            self.ltr_559 = ltr559_import.LTR559()
            self.bme280 = bme280_import.BME280()
            # Setup & Initialize display
            st7735_import = __import__("sensor_modules.drivers.ST7735", fromlist=["ST7735"])
            self.st7735 = st7735_import.ST7735(port=0, cs=1, dc=9, backlight=12, rotation=270, spi_speed_hz=10000000)
            self.st7735.begin()

            # Start thread to turn off display after set amount of seconds (Set after top file imports)
            self.thread_display_power_saving = Thread(target=self._display_timed_off)
            self.thread_display_power_saving.daemon = True
            self.thread_display_power_saving.start()
            logger.sensors_logger.debug("Pimoroni Enviro+ Initialization - OK")
        except Exception as error:
            logger.sensors_logger.error("Pimoroni Enviro+ Initialization - Failed: " + str(error))
            app_config_access.installed_sensors.pimoroni_enviroplus = 0
            app_config_access.installed_sensors.pimoroni_pms5003 = 0
            app_config_access.installed_sensors.has_display = 0
            app_config_access.installed_sensors.has_env_temperature = 0
            app_config_access.installed_sensors.has_pressure = 0
            app_config_access.installed_sensors.has_humidity = 0
            app_config_access.installed_sensors.has_lumen = 0
            app_config_access.installed_sensors.has_distance = 0
            app_config_access.installed_sensors.has_gas = 0
            app_config_access.installed_sensors.has_particulate_matter = 0

        if app_config_access.installed_sensors.has_particulate_matter:
            try:
                pms5003_import = __import__("sensor_modules.drivers.pms5003", fromlist=["PMS5003"])
                self._enable_psm5003_serial()
                self.enviro_plus_pm_access = pms5003_import.PMS5003()
                self.thread_pm_keep_alive = Thread(target=self._readings_keep_alive)
                self.thread_pm_keep_alive.daemon = True
                self.thread_pm_keep_alive.start()
                logger.sensors_logger.debug("Pimoroni Enviro+ PMS5003 Initialization - OK")
            except Exception as error:
                logger.sensors_logger.error("Pimoroni Enviro+ PMS5003 Initialization - Failed: " + str(error))
                app_config_access.installed_sensors.pimoroni_pms5003 = 0

    def _display_timed_off(self):
        while True:
            if self.display_is_on:
                if self.display_off_count > turn_off_display_seconds:
                    self.st7735.set_backlight(0)
                    self.display_is_on = False
                else:
                    self.display_off_count += 1
            time.sleep(1)

    def _readings_keep_alive(self):
        logger.sensors_logger.debug("Pimoroni Enviro+ PMS5003 Particulate Matter & Gas keep alive started")
        while True:
            self.particulate_matter_data()
            time.sleep(1)

    # Displays text on the 0.96" LCD
    def display_text(self, message):
        if not self.display_in_use:
            self.display_in_use = True
            message_img = Image.new('RGB', (self.st7735.width, self.st7735.height), color=(0, 0, 0))
            blank_img = message_img
            draw = ImageDraw.Draw(message_img)

            self.st7735.set_backlight(1)
            self.display_off_count = 0
            self.display_is_on = True

            size_x, size_y = draw.textsize(message, self.font)
            text_x = 160
            text_y = (80 - size_y) // 2

            t_start = time.time()
            try:
                while self.display_off_count < turn_off_display_seconds and self.display_is_on:
                    x = (time.time() - t_start) * 80
                    x %= (size_x + 160)
                    draw.rectangle((0, 0, 160, 80), (0, 0, 0))
                    draw.text((int(text_x - x), text_y), message, font=self.font, fill=(255, 255, 255))
                    self.st7735.display(message_img)
                    time.sleep(0.1)
                self.st7735.display(blank_img)
            except Exception as error:
                logger.sensors_logger.error("Pimoroni Enviro+ Display - Failed: " + str(error))
            self.display_in_use = False
        else:
            logger.sensors_logger.debug("Unable to display message on Pimoroni Enviro+.  Already in use.")

    def temperature(self):
        """ Returns Temperature as a Float. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        try:
            temp_var = float(self.bme280.get_temperature())
        except Exception as error:
            temp_var = 0.0
            logger.sensors_logger.error("Pimoroni Enviro+ Temperature - Failed: " + str(error))
        self.sensor_in_use = False
        return round(temp_var, round_decimal_to)

    def pressure(self):
        """ Returns Pressure as a Integer. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        try:
            pressure_hpa = self.bme280.get_pressure()
        except Exception as error:
            pressure_hpa = 0.0
            logger.sensors_logger.error("Pimoroni Enviro+ Pressure - Failed: " + str(error))
        self.sensor_in_use = False
        return int(pressure_hpa)

    def altitude(self):
        """ Returns Altitude as a Float. """
        # This should probably have a baseline of one sample every second for 100 seconds, but have it's own thread
        # Having it's own thread should allow the program to continue while waiting for this
        # Replace "pressure" with a baseline of the sum of 100 divided by the length 100
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        try:
            var_altitude = self.bme280.get_altitude()
        except Exception as error:
            var_altitude = 0.0
            logger.sensors_logger.error("Pimoroni Enviro+ Altitude - Failed: " + str(error))
        self.sensor_in_use = False
        return round(var_altitude, round_decimal_to)

    def humidity(self):
        """ Returns Humidity as a Float. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        try:
            var_humidity = self.bme280.get_humidity()
        except Exception as error:
            var_humidity = 0.0
            logger.sensors_logger.error("Pimoroni Enviro+ Humidity - Failed: " + str(error))
        self.sensor_in_use = False
        return round(var_humidity, round_decimal_to)

    def lumen(self):
        """ Returns Lumen as a Float. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        try:
            lumen = float(self.ltr_559.get_lux())
        except Exception as error:
            logger.sensors_logger.error("Pimoroni Enviro+ Lumen - Failed: " + str(error))
            lumen = 0.0
        self.sensor_in_use = False
        return round(lumen, round_decimal_to)

    def distance(self):
        """ Returns distance in cm?. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec)
        self.sensor_in_use = True
        try:
            distance = float(self.ltr_559.get_proximity())
        except Exception as error:
            logger.sensors_logger.error("Pimoroni Enviro+ Proximity - Failed: " + str(error))
            distance = 0.0
        self.sensor_in_use = False
        return round(distance, round_decimal_to)

    def gas_data(self):
        """ Returns 3 gas readings Oxidised, Reduced and nh3 as a list. """
        while self.sensor_in_use:
            time.sleep(pause_sensor_during_access_sec_gas)
        self.sensor_in_use = True
        try:
            enviro_plus_gas_data = self.gas_access.read_all()
            oxidised = enviro_plus_gas_data.oxidising / 1000
            reduced = enviro_plus_gas_data.reducing / 1000
            nh3 = enviro_plus_gas_data.nh3 / 1000

            gas_list_oxidised_reduced_nh3 = [round(oxidised, round_decimal_to),
                                             round(reduced, round_decimal_to),
                                             round(nh3, round_decimal_to)]

        except Exception as error:
            logger.sensors_logger.error("Pimoroni Enviro+ GAS - Failed: " + str(error))
            gas_list_oxidised_reduced_nh3 = [0.0, 0.0, 0.0]
        self.sensor_in_use = False
        return gas_list_oxidised_reduced_nh3

    def particulate_matter_data(self):
        """ Returns 3 Particulate Matter readings pm1, pm25 and pm10 as a list. """
        if (time.time() - self.pm_readings_last_updated) > readings_update_threshold_sec:
            update_readings = True
            while self.sensor_in_use:
                update_readings = False
                time.sleep(pause_sensor_during_access_sec_pm)
            if update_readings:
                self.sensor_in_use = True
                try:
                    enviro_plus_pm_data = self.enviro_plus_pm_access.read()
                    self.pm1 = enviro_plus_pm_data.pm_ug_per_m3(1.0)
                    self.pm25 = enviro_plus_pm_data.pm_ug_per_m3(2.5)
                    self.pm10 = enviro_plus_pm_data.pm_ug_per_m3(10)
                    self.pm_readings_last_updated = time.time()
                except Exception as error:
                    logger.sensors_logger.error("Pimoroni Enviro+ Particulate Matter Update - Failed: " + str(error))
                self.sensor_in_use = False
        return [round(self.pm1, round_decimal_to),
                round(self.pm25, round_decimal_to),
                round(self.pm10, round_decimal_to)]

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
            logger.sensors_logger.error("Pimoroni Enviro+ PSM5003 Enable Serial - Failed: " + str(error))
