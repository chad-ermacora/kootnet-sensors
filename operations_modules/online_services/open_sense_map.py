"""
    KootNet Sensors is a collection of programs and scripts to deploy,
    interact with, and collect readings from various Sensors.
    Copyright (C) 2018  Chad Ermacora  chad.ermacora@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import requests
import os
from time import sleep
from operations_modules import logger
from operations_modules import file_locations
from operations_modules import app_generic_functions
from operations_modules import app_config_access
from operations_modules import app_cached_variables

# Weather Underground URL Variables
open_sense_map_main_url_start = "https://api.opensensemap.org/boxes"
open_sense_map_login_url = "https://api.opensensemap.org/users/sign-in"
open_sense_map_refresh_login_url = "https://api.opensensemap.org/users/refresh-auth"


class CreateOpenSenseMapConfig:
    """ Creates a Open Sense Map Configuration object. """

    def __init__(self):
        self.sensor_access = None

        self.login_json_web_token = ""
        self.refresh_json_web_token = ""

        self.open_sense_map_enabled = 0
        self.sense_box_id = "NA"
        self.interval_seconds = 900
        self.sensor_location_type = "outdoor"  # Options are indoor, outdoor, mobile, unknown
        self.sensor_location_coordinates = {"lat": 0.0, "lng": 0.0, "height": 0.0}
        self.open_sense_map_grouptag = ""

        self.manual_sensor_ids_enabled = 0

        self.temperature_id = ""
        self.pressure_id = ""
        self.altitude_id = ""
        self.humidity_id = ""
        self.gas_index_id = ""
        self.gas_oxidised_id = ""
        self.gas_reduced_id = ""
        self.gas_nh3_id = ""
        self.pm1_id = ""
        self.pm2_5_id = ""
        self.pm10_id = ""
        self.lumen_id = ""

        self.red_id = ""
        self.orange_id = ""
        self.yellow_id = ""
        self.green_id = ""
        self.blue_id = ""
        self.violet_id = ""

        self.ultra_violet_index_id = ""
        self.ultra_violet_a_id = ""
        self.ultra_violet_b_id = ""

    def get_configuration_str(self):
        """ Returns Open Sense Map settings ready to be written to the configuration file. """
        config_str = "Enable = 1 & Disable = 0\n" + \
                     str(self.open_sense_map_enabled) + " = Enable Open Sense Map\n" + \
                     str(self.interval_seconds) + " = Send to Server in Seconds\n" + \
                     str(self.sensor_location_type) + " = Sensor is Outdoors\n" + \
                     str(self.sense_box_id) + " = Open Sense Map Sense ID"

        return config_str

    def update_open_sense_map_html(self, html_request):
        """ Updates & Writes Open Sense Map settings based on provided HTML request. """
        if html_request.form.get("enable_weather_underground") is not None:
            self.open_sense_map_enabled = 1
            if html_request.form.get("weather_underground_outdoor") is not None:
                self.sensor_location_type = 1
            else:
                self.sensor_location_type = 0
        else:
            self.open_sense_map_enabled = 0

        if html_request.form.get("weather_underground_interval") is not None:
            self.interval_seconds = float(html_request.form.get("weather_underground_interval"))
        if html_request.form.get("station_id") is not None:
            self.sense_box_id = html_request.form.get("station_id").strip()

        self.write_config_to_file()

    def update_settings_from_file(self):
        """
        Updates Open Sense Map settings based on saved configuration file.  Creates Default file if missing.
        """
        if os.path.isfile(file_locations.osm_config):
            loaded_configuration_raw = app_generic_functions.get_file_content(file_locations.osm_config)
            configuration_lines = loaded_configuration_raw.split("\n")
            try:
                if int(configuration_lines[1][0]):
                    self.open_sense_map_enabled = 1
                else:
                    self.open_sense_map_enabled = 0

                try:
                    self.interval_seconds = float(configuration_lines[2].split("=")[0].strip())
                except Exception as error:
                    logger.primary_logger.warning("Open Sense Map Interval Error from file - " + str(error))
                    self.interval_seconds = 300

                if int(configuration_lines[3][0]):
                    self.sensor_location_type = 1
                else:
                    self.sensor_location_type = 0

                self.sense_box_id = configuration_lines[4].split("=")[0].strip()
                self.station_key = configuration_lines[5].split("=")[0].strip()
            except Exception as error:
                self.write_config_to_file()
                logger.primary_logger.warning("Problem loading Open Sense Map Configuration file - " +
                                              "Using 1 or more Defaults: " + str(error))
        else:
            logger.primary_logger.warning("No Open Sense Map configuration file found - Saving Default")
            self.write_config_to_file()

    def write_config_to_file(self):
        """ Writes current Open Sense Map settings to file. """
        config_str = self.get_configuration_str()
        app_generic_functions.write_file_to_disk(file_locations.osm_config, config_str)

    def start_open_sense_map(self):
        """ Sends compatible sensor readings to Open Sense Map every X seconds based on set Interval. """
        if not app_config_access.open_sense_map_thread_running:
            app_config_access.open_sense_map_thread_running = True
            # Sleep 5 seconds before starting
            # So it doesn't try to access the sensors at the same time as the recording services on boot
            sleep(8)

            url = open_sense_map_main_url_start + "/" + self.sense_box_id + "/data"
            url_header = {"content-type": "application/json"}

            round_decimal_to = 5
            while True:
                body_json = {}
                try:
                    if app_config_access.installed_sensors.has_env_temperature:
                        if self.temperature_id != "":
                            env_temperature = self.sensor_access.get_sensor_temperature()
                            try:
                                if app_config_access.current_config.enable_custom_temp:
                                    env_temperature = round(env_temperature +
                                                            app_config_access.current_config.temperature_offset,
                                                            round_decimal_to)
                            except Exception as error:
                                logger.network_logger.warning("Open Sense Map: Env Offset Error - " + str(error))
                            body_json[self.temperature_id] = str(env_temperature)

                    if app_config_access.installed_sensors.has_pressure:
                        if self.pressure_id != "":
                            body_json[self.pressure_id] = str(self.sensor_access.get_pressure())
                    if app_config_access.installed_sensors.has_altitude:
                        if self.altitude_id != "":
                            body_json[self.altitude_id] = str(self.sensor_access.get_altitude())
                    if app_config_access.installed_sensors.has_humidity:
                        if self.humidity_id != "":
                            body_json[self.humidity_id] = str(self.sensor_access.get_humidity())
                    if app_config_access.installed_sensors.has_gas:
                        gas_index = self.sensor_access.get_gas_resistance_index()
                        gas_oxidised = self.sensor_access.get_gas_oxidised()
                        gas_reduced = self.sensor_access.get_gas_reduced()
                        gas_nh3 = self.sensor_access.get_gas_nh3()
                        if self.gas_index_id != "" and self.sensor_access.valid_sensor_reading(gas_index):
                            body_json[self.gas_index_id] = str(gas_index)
                        if self.gas_oxidised_id != "" and self.sensor_access.valid_sensor_reading(gas_oxidised):
                            body_json[self.gas_oxidised_id] = str(gas_oxidised)
                        if self.gas_reduced_id != "" and self.sensor_access.valid_sensor_reading(gas_reduced):
                            body_json[self.gas_reduced_id] = str(gas_reduced)
                        if self.gas_nh3_id != "" and self.sensor_access.valid_sensor_reading(gas_nh3):
                            body_json[self.gas_nh3_id] = str(gas_nh3)
                    if app_config_access.installed_sensors.has_lumen:
                        if self.lumen_id != "":
                            body_json[self.lumen_id] = str(self.sensor_access.get_lumen())
                    if app_config_access.installed_sensors.has_particulate_matter:
                        pm1 = self.sensor_access.get_particulate_matter_1()
                        pm2_5 = self.sensor_access.get_particulate_matter_2_5()
                        pm10 = self.sensor_access.get_particulate_matter_10()
                        if self.pm1_id != "" and self.sensor_access.valid_sensor_reading(pm1):
                            body_json[self.pm1_id] = str(pm1)
                        if self.pm2_5_id != "" and self.sensor_access.valid_sensor_reading(pm2_5):
                            body_json[self.pm2_5_id] = str(pm2_5)
                        if self.pm10_id != "" and self.sensor_access.valid_sensor_reading(pm10):
                            body_json[self.pm10_id] = str(pm10)

                    if body_json is not None:
                        html_get_response = requests.post(url=url, headers=url_header, json=body_json)
                        if html_get_response.status_code == 201:
                            logger.network_logger.info("Sensors sent to Open Sense Map OK")
                        elif html_get_response.status_code == 403:
                            logger.network_logger.error("Open Sense Map: Invalid JWT - Please sign in")
                            sleep(3600)
                        elif html_get_response.status_code == 415:
                            logger.network_logger.error("Open Sense Map: - Invalid or Missing content type")
                        else:
                            logger.network_logger.error(
                                "Open Sense Map: Unknown Error " + str(html_get_response.status_code))
                            logger.network_logger.error("Open Sense Map: " + str(html_get_response.text))
                    else:
                        logger.network_logger.warning("Open Sense Map not Updated - No Compatible Sensors")
                        while True:
                            sleep(3600)
                except Exception as error:
                    logger.network_logger.error("Error sending data to Open Sense Map: " + str(error))
                sleep(self.interval_seconds)

    def add_sensor_to_account(self):
        url = open_sense_map_main_url_start
        url_header = {"Authorization": "Bearer " + self.login_json_web_token, "content-type": "application/json"}

        body_json = {"name": app_cached_variables.hostname}
        if self.open_sense_map_grouptag:
            body_json["grouptag"] = self.open_sense_map_grouptag
        body_json["exposure"] = self.sensor_location_type
        if self.sensor_location_coordinates["lat"] != 0.0 and self.sensor_location_coordinates["lng"] != 0.0:
            body_json["location"] = self.sensor_location_coordinates
        body_json["sensors"] = self._get_osm_registration_sensors()

        html_get_response = requests.post(url=url, headers=url_header, json=body_json)
        if html_get_response.status_code == 201:
            logger.network_logger.info("Sensors sent to Open Sense Map OK")
        elif html_get_response.status_code == 403:
            logger.network_logger.error("Open Sense Map: Invalid JWT - Please sign in")
            sleep(3600)
        elif html_get_response.status_code == 415:
            logger.network_logger.error("Open Sense Map: - Invalid or Missing content type")
        else:
            logger.network_logger.error("Open Sense Map: Unknown Error " + str(html_get_response.status_code))
            logger.network_logger.error("Open Sense Map: " + str(html_get_response.text))

    @staticmethod
    def _get_osm_registration_sensors():
        sensor_types = []
        if app_config_access.installed_sensors.pimoroni_as7262:
            sensor_types.append({
                "title": "Red",
                "unit": "lm",
                "sensorType": "PimoroniAS7262"
            })
            sensor_types.append({
                "title": "Orange",
                "unit": "lm",
                "sensorType": "PimoroniAS7262"
            })
            sensor_types.append({
                "title": "Yellow",
                "unit": "lm",
                "sensorType": "PimoroniAS7262"
            })
            sensor_types.append({
                "title": "Green",
                "unit": "lm",
                "sensorType": "PimoroniAS7262"
            })
            sensor_types.append({
                "title": "Blue",
                "unit": "lm",
                "sensorType": "PimoroniAS7262"
            })
            sensor_types.append({
                "title": "Violet",
                "unit": "lm",
                "sensorType": "PimoroniAS7262"
            })
        if app_config_access.installed_sensors.pimoroni_bh1745:
            sensor_types.append({
                "title": "Lumen",
                "unit": "lm",
                "sensorType": "PimoroniBH1745"
            })
            sensor_types.append({
                "title": "Red",
                "unit": "lm",
                "sensorType": "PimoroniBH1745"
            })
            sensor_types.append({
                "title": "Green",
                "unit": "lm",
                "sensorType": "PimoroniBH1745"
            })
            sensor_types.append({
                "title": "Blue",
                "unit": "lm",
                "sensorType": "PimoroniBH1745"
            })
        if app_config_access.installed_sensors.pimoroni_bme680:
            sensor_types.append({
                "title": "Temperature",
                "unit": "°C",
                "sensorType": "PimoroniBME680"
            })
            sensor_types.append({
                "title": "Pressure",
                "unit": "hPa",
                "sensorType": "PimoroniBME680"
            })
            sensor_types.append({
                "title": "Humidity",
                "unit": "%RH",
                "sensorType": "PimoroniBME680"
            })
            sensor_types.append({
                "title": "GAS",
                "unit": "kΩ",
                "sensorType": "PimoroniBME680"
            })
        if app_config_access.installed_sensors.pimoroni_bmp280:
            sensor_types.append({
                "title": "Temperature",
                "unit": "°C",
                "sensorType": "PimoroniBMP280"
            })
            sensor_types.append({
                "title": "Pressure",
                "unit": "hPa",
                "sensorType": "PimoroniBMP280"
            })
            sensor_types.append({
                "title": "Altitude",
                "unit": "m",
                "sensorType": "PimoroniBMP280"
            })
        if app_config_access.installed_sensors.pimoroni_enviro:
            sensor_types.append({
                "title": "Temperature",
                "unit": "°C",
                "sensorType": "PimoroniEnviroPHAT"
            })
            sensor_types.append({
                "title": "Pressure",
                "unit": "hPa",
                "sensorType": "PimoroniEnviroPHAT"
            })
            sensor_types.append({
                "title": "Lumen",
                "unit": "lm",
                "sensorType": "PimoroniEnviroPHAT"
            })
            sensor_types.append({
                "title": "Red",
                "unit": "lm",
                "sensorType": "PimoroniEnviroPHAT"
            })
            sensor_types.append({
                "title": "Green",
                "unit": "lm",
                "sensorType": "PimoroniEnviroPHAT"
            })
            sensor_types.append({
                "title": "Blue",
                "unit": "lm",
                "sensorType": "PimoroniEnviroPHAT"
            })
        if app_config_access.installed_sensors.pimoroni_enviroplus:
            sensor_types.append({
                "title": "Temperature",
                "unit": "°C",
                "sensorType": "PimoroniEnviroPlus"
            })
            sensor_types.append({
                "title": "Pressure",
                "unit": "hPa",
                "sensorType": "PimoroniEnviroPlus"
            })
            sensor_types.append({
                "title": "Humidity",
                "unit": "%RH",
                "sensorType": "PimoroniEnviroPlus"
            })
            sensor_types.append({
                "title": "Lumen",
                "unit": "lm",
                "sensorType": "PimoroniEnviroPlus"
            })
            sensor_types.append({
                "title": "Oxidised",
                "unit": "kΩ",
                "sensorType": "PimoroniEnviroPlus"
            })
            sensor_types.append({
                "title": "Reduced",
                "unit": "kΩ",
                "sensorType": "PimoroniEnviroPlus"
            })
            sensor_types.append({
                "title": "nh3",
                "unit": "kΩ",
                "sensorType": "PimoroniEnviroPlus"
            })
        if app_config_access.installed_sensors.pimoroni_pms5003:
            sensor_types.append({
                "title": "PM1",
                "unit": "µg/m³",
                "sensorType": "PSM5003"
            })
            sensor_types.append({
                "title": "PM2.5",
                "unit": "µg/m³",
                "sensorType": "PSM5003"
            })
            sensor_types.append({
                "title": "PM10",
                "unit": "µg/m³",
                "sensorType": "PSM5003"
            })
        if app_config_access.installed_sensors.pimoroni_ltr_559:
            sensor_types.append({
                "title": "Lumen",
                "unit": "lm",
                "sensorType": "PimoroniLTR559"
            })
        if app_config_access.installed_sensors.pimoroni_veml6075:
            sensor_types.append({
                "title": "UltraVioletIndex",
                "unit": "UV",
                "sensorType": "PimoroniVEML6075"
            })
            sensor_types.append({
                "title": "UltraVioletA",
                "unit": "UVA",
                "sensorType": "PimoroniVEML6075"
            })
            sensor_types.append({
                "title": "UltraVioletB",
                "unit": "UVB",
                "sensorType": "PimoroniVEML6075"
            })
        if app_config_access.installed_sensors.raspberry_pi_sense_hat:
            sensor_types.append({
                "title": "Temperature",
                "unit": "°C",
                "sensorType": "RPiSenseHAT"
            })
            sensor_types.append({
                "title": "Pressure",
                "unit": "hPa",
                "sensorType": "RPiSenseHAT"
            })
            sensor_types.append({
                "title": "Humidity",
                "unit": "%RH",
                "sensorType": "RPiSenseHAT"
            })
        return sensor_types

    def update_json_web_tokens(self, account_email, account_password):
        response = requests.post(url=open_sense_map_login_url,
                                 json={"email": account_email, "password": account_password})
        if response.status_code == 200:
            try:
                self.login_json_web_token = response.json()["token"]
                self.refresh_json_web_token = response.json()["refreshToken"]
                logger.network_logger.error("Token: " + str(self.login_json_web_token))
            except Exception as error:
                logger.network_logger.warning("Open Sense Map Token get fail: " + str(error))
        elif response.status_code == 403:
            logger.network_logger.warning("Open Sense Map: Login Failed")
        else:
            logger.network_logger.warning("Open Sense Map: Something... ")
