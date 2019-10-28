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
from time import sleep
from operations_modules import logger
from operations_modules import app_cached_variables
from operations_modules.app_config_access import current_config, installed_sensors, open_sense_map_config
from operations_modules.app_validation_checks import valid_sensor_reading
from sensor_modules import sensor_access


def start_open_sense_map():
    """ Sends compatible sensor readings to Open Sense Map every X seconds based on set Interval. """
    if open_sense_map_config.sense_box_id != "":
        url = open_sense_map_config.open_sense_map_main_url_start + "/" + open_sense_map_config.sense_box_id + "/data"
        url_header = {"content-type": "application/json"}

        round_decimal_to = 5
        while True:
            body_json = {}
            try:
                if installed_sensors.has_env_temperature:
                    if open_sense_map_config.temperature_id != "":
                        try:
                            env_temperature = sensor_access.get_sensor_temperature()
                            if current_config.enable_custom_temp:
                                env_temperature = round(env_temperature +
                                                        current_config.temperature_offset,
                                                        round_decimal_to)
                        except Exception as error:
                            logger.network_logger.warning("Open Sense Map - Env Temperature Error: " + str(error))
                            env_temperature = 0.0
                        body_json[open_sense_map_config.temperature_id] = str(env_temperature)

                if installed_sensors.has_pressure:
                    if open_sense_map_config.pressure_id != "":
                        body_json[open_sense_map_config.pressure_id] = str(sensor_access.get_pressure())
                if installed_sensors.has_altitude:
                    if open_sense_map_config.altitude_id != "":
                        body_json[open_sense_map_config.altitude_id] = str(sensor_access.get_altitude())
                if installed_sensors.has_humidity:
                    if open_sense_map_config.humidity_id != "":
                        body_json[open_sense_map_config.humidity_id] = str(sensor_access.get_humidity())
                if installed_sensors.has_gas:
                    gas_voc = sensor_access.get_gas_resistance_index()
                    gas_oxidised = sensor_access.get_gas_oxidised()
                    gas_reduced = sensor_access.get_gas_reduced()
                    gas_nh3 = sensor_access.get_gas_nh3()
                    if open_sense_map_config.gas_voc_id != "" and valid_sensor_reading(gas_voc):
                        body_json[open_sense_map_config.gas_voc_id] = str(gas_voc)
                    if open_sense_map_config.gas_oxidised_id != "" and valid_sensor_reading(gas_oxidised):
                        body_json[open_sense_map_config.gas_oxidised_id] = str(gas_oxidised)
                    if open_sense_map_config.gas_reduced_id != "" and valid_sensor_reading(gas_reduced):
                        body_json[open_sense_map_config.gas_reduced_id] = str(gas_reduced)
                    if open_sense_map_config.gas_nh3_id != "" and valid_sensor_reading(gas_nh3):
                        body_json[open_sense_map_config.gas_nh3_id] = str(gas_nh3)
                if installed_sensors.has_lumen:
                    if open_sense_map_config.lumen_id != "":
                        body_json[open_sense_map_config.lumen_id] = str(sensor_access.get_lumen())
                if installed_sensors.has_particulate_matter:
                    pm1 = sensor_access.get_particulate_matter_1()
                    pm2_5 = sensor_access.get_particulate_matter_2_5()
                    pm10 = sensor_access.get_particulate_matter_10()
                    if open_sense_map_config.pm1_id != "" and valid_sensor_reading(pm1):
                        body_json[open_sense_map_config.pm1_id] = str(pm1)
                    if open_sense_map_config.pm2_5_id != "" and valid_sensor_reading(pm2_5):
                        body_json[open_sense_map_config.pm2_5_id] = str(pm2_5)
                    if open_sense_map_config.pm10_id != "" and valid_sensor_reading(pm10):
                        body_json[open_sense_map_config.pm10_id] = str(pm10)
                colours = sensor_access.get_ems()
                if installed_sensors.has_red:
                    if open_sense_map_config.red_id != "":
                        body_json[open_sense_map_config.red_id] = str(colours[0])
                if installed_sensors.has_orange:
                    if open_sense_map_config.orange_id != "":
                        body_json[open_sense_map_config.orange_id] = str(colours[1])
                if installed_sensors.has_yellow:
                    if open_sense_map_config.yellow_id != "":
                        body_json[open_sense_map_config.yellow_id] = str(colours[2])
                if installed_sensors.has_green:
                    if open_sense_map_config.green_id != "":
                        body_json[open_sense_map_config.green_id] = str(colours[3])
                if installed_sensors.has_blue:
                    if open_sense_map_config.blue_id != "":
                        body_json[open_sense_map_config.blue_id] = str(colours[4])
                if installed_sensors.has_violet:
                    if open_sense_map_config.violet_id != "":
                        body_json[open_sense_map_config.violet_id] = str(colours[5])
                if installed_sensors.has_ultra_violet:
                    if open_sense_map_config.ultra_violet_index_id != "":
                        body_json[open_sense_map_config.ultra_violet_index_id] = str(sensor_access.get_ultra_violet_index())
                    if open_sense_map_config.ultra_violet_a_id != "":
                        body_json[open_sense_map_config.ultra_violet_a_id] = str(sensor_access.get_ultra_violet_a())
                    if open_sense_map_config.ultra_violet_b_id != "":
                        body_json[open_sense_map_config.ultra_violet_b_id] = str(sensor_access.get_ultra_violet_b())

                if len(body_json) > 0:
                    html_get_response = requests.post(url=url, headers=url_header, json=body_json)
                    status_code = str(html_get_response.status_code)
                    response_text = str(html_get_response.text)
                    if html_get_response.status_code == 201:
                        logger.network_logger.debug("Open Sense Map - Sent OK - Status Code: " + status_code)
                    elif html_get_response.status_code == 415:
                        logger.network_logger.error("Open Sense Map: Invalid or Missing content type")
                    else:
                        log_msg = "Open Sense Map - Unknown Error " + status_code + ": " + response_text
                        logger.network_logger.error(log_msg)
                else:
                    log_msg = "Open Sense Map - No further updates will be attempted: " + \
                              "No Compatible Sensors or Missing Sensor IDs"
                    logger.network_logger.warning(log_msg)
                    while True:
                        sleep(3600)
            except Exception as error:
                logger.network_logger.error("Open Sense Map - Error sending data")
                logger.network_logger.debug("Open Sense Map - Detailed Error: " + str(error))
            sleep(open_sense_map_config.interval_seconds)


def add_sensor_to_account(html_request):
    url = open_sense_map_config.open_sense_map_main_url_start
    bad_location_message = "Open Sense Map - Sensor Registration: Invalid Location Setting"
    try:
        username = html_request.form.get("osm_account_username").strip()
        password = html_request.form.get("osm_account_password").strip()
        login_token = get_json_web_login_token(username, password)
        if login_token is not None:
            url_header = {"Authorization": "Bearer " + login_token,
                          "content-type": "application/json"}
            body_json = {"name": app_cached_variables.hostname,
                         "exposure": html_request.form.get("osm_location_type").strip()}

            grouptag = html_request.form.get("osm_grouptag").strip()
            if grouptag is not None and grouptag != "":
                body_json["grouptag"] = grouptag
            location_extract = html_request.form.get("osm_location_coordinates").split(",")
            body_json["location"] = {"lat": float(location_extract[0].strip()),
                                     "lng": float(location_extract[1].strip()),
                                     "height": float(location_extract[2].strip())}
            body_json["sensors"] = _get_osm_registration_sensors()

            html_get_response = requests.post(url=url, headers=url_header, json=body_json)
            if html_get_response.status_code == 201:
                logger.network_logger.info("Registered Sensor on Open Sense Map OK")
                return 201
            elif html_get_response.status_code == 415:
                logger.network_logger.error("Open Sense Map error: Invalid or Missing content type")
                return 415
            elif html_get_response.status_code == 422:
                logger.network_logger.error(bad_location_message)
                return 422
            else:
                status_code = str(html_get_response.status_code)
                response_text = str(html_get_response.text)
                log_msg = "Open Sense Map - Sensor Registration Unknown Error " + status_code + ": " + response_text
                logger.network_logger.error(log_msg)
                return "UnknownError"
        else:
            logger.network_logger.error("Open Sense Map - Error Adding Sensor to Account: Login Failed")
            return "FailedLogin"
    except IndexError:
        logger.network_logger.error(bad_location_message)
        return 422
    except ValueError:
        logger.network_logger.error(bad_location_message)
        return 422
    except Exception as error:
        logger.network_logger.error("Open Sense Map - Error Adding Sensor to Account: " + str(error))
        return str(error)


def _get_osm_registration_sensors():
    sensor_types = []
    if installed_sensors.raspberry_pi_sense_hat:
        sensor_types.append({
            "title": "Temperature",
            "unit": "°C",
            "sensorType": "RPiSenseHAT",
            "icon": "osem-thermometer"
        })
        sensor_types.append({
            "title": "Pressure",
            "unit": "hPa",
            "sensorType": "RPiSenseHAT",
            "icon": "osem-barometer"
        })
        sensor_types.append({
            "title": "Humidity",
            "unit": "%RH",
            "sensorType": "RPiSenseHAT",
            "icon": "osem-humidity"
        })
    if installed_sensors.pimoroni_enviro:
        sensor_types.append({
            "title": "Temperature",
            "unit": "°C",
            "sensorType": "PimoroniEnviroPHAT",
            "icon": "osem-thermometer"
        })
        sensor_types.append({
            "title": "Pressure",
            "unit": "hPa",
            "sensorType": "PimoroniEnviroPHAT",
            "icon": "osem-barometer"
        })
        sensor_types.append({
            "title": "Lumen",
            "unit": "lm",
            "sensorType": "PimoroniEnviroPHAT",
            "icon": "osem-brightness"
        })
        sensor_types.append({
            "title": "Red",
            "unit": "lm",
            "sensorType": "PimoroniEnviroPHAT",
            "icon": "osem-brightness"
        })
        sensor_types.append({
            "title": "Green",
            "unit": "lm",
            "sensorType": "PimoroniEnviroPHAT",
            "icon": "osem-brightness"
        })
        sensor_types.append({
            "title": "Blue",
            "unit": "lm",
            "sensorType": "PimoroniEnviroPHAT",
            "icon": "osem-brightness"
        })
    if installed_sensors.pimoroni_enviroplus:
        sensor_types.append({
            "title": "Temperature",
            "unit": "°C",
            "sensorType": "PimoroniEnviroPlus",
            "icon": "osem-thermometer"
        })
        sensor_types.append({
            "title": "Pressure",
            "unit": "hPa",
            "sensorType": "PimoroniEnviroPlus",
            "icon": "osem-barometer"
        })
        sensor_types.append({
            "title": "Humidity",
            "unit": "%RH",
            "sensorType": "PimoroniEnviroPlus",
            "icon": "osem-humidity"
        })
        sensor_types.append({
            "title": "Lumen",
            "unit": "lm",
            "sensorType": "PimoroniEnviroPlus",
            "icon": "osem-brightness"
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
    if installed_sensors.pimoroni_pms5003:
        sensor_types.append({
            "title": "PM1",
            "unit": "µg/m³",
            "sensorType": "PSM5003",
            "icon": "osem-cloud"
        })
        sensor_types.append({
            "title": "PM2.5",
            "unit": "µg/m³",
            "sensorType": "PSM5003",
            "icon": "osem-cloud"
        })
        sensor_types.append({
            "title": "PM10",
            "unit": "µg/m³",
            "sensorType": "PSM5003",
            "icon": "osem-cloud"
        })
    if installed_sensors.pimoroni_bme680:
        sensor_types.append({
            "title": "Temperature",
            "unit": "°C",
            "sensorType": "PimoroniBME680",
            "icon": "osem-thermometer"
        })
        sensor_types.append({
            "title": "Pressure",
            "unit": "hPa",
            "sensorType": "PimoroniBME680",
            "icon": "osem-barometer"
        })
        sensor_types.append({
            "title": "Humidity",
            "unit": "%RH",
            "sensorType": "PimoroniBME680",
            "icon": "osem-humidity"
        })
        sensor_types.append({
            "title": "Gas VOC",
            "unit": "kΩ",
            "sensorType": "PimoroniBME680"
        })
    if installed_sensors.pimoroni_bmp280:
        sensor_types.append({
            "title": "Temperature",
            "unit": "°C",
            "sensorType": "PimoroniBMP280",
            "icon": "osem-thermometer"
        })
        sensor_types.append({
            "title": "Pressure",
            "unit": "hPa",
            "sensorType": "PimoroniBMP280",
            "icon": "osem-barometer"
        })
        sensor_types.append({
            "title": "Altitude",
            "unit": "m",
            "sensorType": "PimoroniBMP280"
        })
    if installed_sensors.pimoroni_ltr_559:
        sensor_types.append({
            "title": "Lumen",
            "unit": "lm",
            "sensorType": "PimoroniLTR559",
            "icon": "osem-brightness"
        })
    if installed_sensors.pimoroni_as7262:
        sensor_types.append({
            "title": "Red",
            "unit": "lm",
            "sensorType": "PimoroniAS7262",
            "icon": "osem-brightness"
        })
        sensor_types.append({
            "title": "Orange",
            "unit": "lm",
            "sensorType": "PimoroniAS7262",
            "icon": "osem-brightness"
        })
        sensor_types.append({
            "title": "Yellow",
            "unit": "lm",
            "sensorType": "PimoroniAS7262",
            "icon": "osem-brightness"
        })
        sensor_types.append({
            "title": "Green",
            "unit": "lm",
            "sensorType": "PimoroniAS7262",
            "icon": "osem-brightness"
        })
        sensor_types.append({
            "title": "Blue",
            "unit": "lm",
            "sensorType": "PimoroniAS7262",
            "icon": "osem-brightness"
        })
        sensor_types.append({
            "title": "Violet",
            "unit": "lm",
            "sensorType": "PimoroniAS7262",
            "icon": "osem-brightness"
        })
    if installed_sensors.pimoroni_bh1745:
        sensor_types.append({
            "title": "Lumen",
            "unit": "lm",
            "sensorType": "PimoroniBH1745",
            "icon": "osem-brightness"
        })
        sensor_types.append({
            "title": "Red",
            "unit": "lm",
            "sensorType": "PimoroniBH1745",
            "icon": "osem-brightness"
        })
        sensor_types.append({
            "title": "Green",
            "unit": "lm",
            "sensorType": "PimoroniBH1745",
            "icon": "osem-brightness"
        })
        sensor_types.append({
            "title": "Blue",
            "unit": "lm",
            "sensorType": "PimoroniBH1745",
            "icon": "osem-brightness"
        })
    if installed_sensors.pimoroni_veml6075:
        sensor_types.append({
            "title": "UltraVioletIndex",
            "unit": "UV",
            "sensorType": "PimoroniVEML6075",
            "icon": "osem-brightness"
        })
        sensor_types.append({
            "title": "UltraVioletA",
            "unit": "UVA",
            "sensorType": "PimoroniVEML6075",
            "icon": "osem-brightness"
        })
        sensor_types.append({
            "title": "UltraVioletB",
            "unit": "UVB",
            "sensorType": "PimoroniVEML6075",
            "icon": "osem-brightness"
        })
    return sensor_types


def get_json_web_login_token(account_email, account_password):
    response = requests.post(url=open_sense_map_config.open_sense_map_login_url,
                             json={"email": account_email, "password": account_password})
    if response.status_code == 200:
        try:
            logger.network_logger.debug("Open Sense Map - Get Token: OK")
            return response.json()["token"]
        except Exception as error:
            logger.network_logger.warning("Open Sense Map - Get Token Failed: " + str(error))
    elif response.status_code == 403:
        logger.network_logger.debug("Open Sense Map - Get Token: Login Failed")
    else:
        logger.network_logger.warning("Open Sense Map - Get Token: Login went wrong somehow...")
