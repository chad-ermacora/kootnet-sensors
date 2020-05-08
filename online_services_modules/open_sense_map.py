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
from operations_modules.app_cached_variables import no_sensor_present, database_variables, hostname
from operations_modules.app_config_access import installed_sensors, open_sense_map_config as osm_config
from sensor_modules import sensor_access


def start_open_sense_map():
    """ Sends compatible sensor readings to Open Sense Map every X seconds based on set Interval. """
    if osm_config.sense_box_id != "":
        url = osm_config.open_sense_map_main_url_start + "/" + osm_config.sense_box_id + "/data"
        url_header = {"content-type": "application/json"}

        while True:
            body_json = {}
            try:
                env_temperature = str(sensor_access.get_sensor_temperature())
                if env_temperature != no_sensor_present and osm_config.temperature_id != "":
                    body_json[osm_config.temperature_id] = env_temperature

                pressure_reading = str(sensor_access.get_pressure())
                if pressure_reading != no_sensor_present and osm_config.pressure_id != "":
                    body_json[osm_config.pressure_id] = pressure_reading

                altitude_reading = str(sensor_access.get_altitude())
                if altitude_reading != no_sensor_present and osm_config.altitude_id != "":
                    body_json[osm_config.altitude_id] = altitude_reading

                humidity_reading = str(sensor_access.get_humidity())
                if humidity_reading != no_sensor_present and osm_config.humidity_id != "":
                    body_json[osm_config.humidity_id] = str(sensor_access.get_humidity())

                gas_readings = sensor_access.get_gas(return_as_dictionary=True)
                if gas_readings != no_sensor_present:
                    if database_variables.gas_resistance_index in gas_readings and osm_config.gas_voc_id != "":
                        gas_voc = gas_readings[database_variables.gas_resistance_index]
                        body_json[osm_config.gas_voc_id] = str(gas_voc)
                    if database_variables.gas_oxidising in gas_readings and osm_config.gas_oxidised_id != "":
                        gas_oxidised = gas_readings[database_variables.gas_oxidising]
                        body_json[osm_config.gas_oxidised_id] = str(gas_oxidised)
                    if database_variables.gas_reducing in gas_readings and osm_config.gas_reduced_id != "":
                        gas_reduced = gas_readings[database_variables.gas_reducing]
                        body_json[osm_config.gas_reduced_id] = str(gas_reduced)
                    if database_variables.gas_nh3 in gas_readings and osm_config.gas_nh3_id != "":
                        gas_nh3 = gas_readings[database_variables.gas_nh3]
                        body_json[osm_config.gas_nh3_id] = str(gas_nh3)

                lumen_reading = str(sensor_access.get_lumen())
                if lumen_reading != no_sensor_present and osm_config.lumen_id != "":
                    body_json[osm_config.lumen_id] = lumen_reading

                pm_readings = sensor_access.get_particulate_matter(return_as_dictionary=True)
                if pm_readings != no_sensor_present:
                    if database_variables.particulate_matter_1 in pm_readings and osm_config.pm1_id != "":
                        pm1 = pm_readings[database_variables.particulate_matter_1]
                        body_json[osm_config.pm1_id] = str(pm1)
                    if database_variables.particulate_matter_2_5 in pm_readings and osm_config.pm2_5_id != "":
                        pm2_5 = pm_readings[database_variables.particulate_matter_2_5]
                        body_json[osm_config.pm2_5_id] = str(pm2_5)
                    if database_variables.particulate_matter_10 in pm_readings and osm_config.pm10_id != "":
                        pm10 = pm_readings[database_variables.particulate_matter_10]
                        body_json[osm_config.pm10_id] = str(pm10)

                colors = sensor_access.get_ems_colors(return_as_dictionary=True)
                if colors != no_sensor_present:
                    if database_variables.red in colors and osm_config.red_id != "":
                        red = colors[database_variables.red]
                        body_json[osm_config.red_id] = str(red)
                    if database_variables.orange in colors and osm_config.orange_id != "":
                        orange = colors[database_variables.orange]
                        body_json[osm_config.orange_id] = str(orange)
                    if database_variables.yellow in colors and osm_config.yellow_id != "":
                        yellow = colors[database_variables.yellow]
                        body_json[osm_config.yellow_id] = str(yellow)
                    if database_variables.green in colors and osm_config.green_id != "":
                        green = colors[database_variables.green]
                        body_json[osm_config.green_id] = str(green)
                    if database_variables.blue in colors and osm_config.blue_id != "":
                        blue = colors[database_variables.blue]
                        body_json[osm_config.blue_id] = str(blue)
                    if database_variables.violet in colors and osm_config.violet_id != "":
                        violet = colors[database_variables.violet]
                        body_json[osm_config.violet_id] = str(violet)

                uv_readings = sensor_access.get_ultra_violet(return_as_dictionary=True)
                if uv_readings != no_sensor_present:
                    if database_variables.ultra_violet_index in uv_readings and osm_config.ultra_violet_index_id != "":
                        uv_index = uv_readings[database_variables.ultra_violet_index]
                        body_json[osm_config.ultra_violet_index_id] = str(uv_index)
                    if database_variables.ultra_violet_a in uv_readings and osm_config.ultra_violet_a_id != "":
                        uv_a = uv_readings[database_variables.ultra_violet_a]
                        body_json[osm_config.ultra_violet_a_id] = str(uv_a)
                    if database_variables.ultra_violet_b in uv_readings and osm_config.ultra_violet_b_id != "":
                        uv_b = uv_readings[database_variables.ultra_violet_b]
                        body_json[osm_config.ultra_violet_b_id] = str(uv_b)

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
            sleep(osm_config.interval_seconds)


def add_sensor_to_account(html_request):
    url = osm_config.open_sense_map_main_url_start
    bad_location_message = "Open Sense Map - Sensor Registration: Invalid Location Setting"
    try:
        username = html_request.form.get("osm_account_username").strip()
        password = html_request.form.get("osm_account_password").strip()
        login_token = get_json_web_login_token(username, password)
        if login_token is not None:
            url_header = {"Authorization": "Bearer " + login_token,
                          "content-type": "application/json"}
            body_json = {"name": hostname,
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
    response = requests.post(url=osm_config.open_sense_map_login_url,
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
