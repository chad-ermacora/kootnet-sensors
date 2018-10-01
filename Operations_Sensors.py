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
import Operations_DB
import Operations_Config
import sensor_modules.Linux_OS
import sensor_modules.RaspberryPi_System
import sensor_modules.RaspberryPi_SenseHAT
import sensor_modules.Pimoroni_BH1745
import sensor_modules.Pimoroni_BME680
import sensor_modules.Pimoroni_Enviro
import sensor_modules.Pimoroni_LSM303D
import sensor_modules.Pimoroni_VL53L1X

installed_sensors = Operations_Config.get_installed_sensors()
installed_config = Operations_Config.get_installed_config()


def print_sql_command_data_to_screen(readings):
    print("\nInterval Types: " + str(readings.sensor_types))
    print("\nInterval Readings: " + str(readings.sensor_readings))


def get_interval_sensor_readings():
    interval_data = Operations_DB.CreateIntervalDatabaseData()

    count = 0
    if installed_sensors.linux_system:
        sensor_os = sensor_modules.Linux_OS.CreateLinuxSystem()
        sensor_system = sensor_modules.RaspberryPi_System.CreateRPSystem()

        tmp_sensor_types = "SensorName, IP, SensorUpTime, SystemTemp"

        tmp_sensor_readings = "'" + str(sensor_os.get_hostname()) + "', '" + \
                              str(sensor_os.get_ip()) + "', '" + \
                              str(sensor_os.get_uptime()) + "', '" + \
                              str(sensor_system.cpu_temperature()) + "'"

        interval_data.sensor_types = interval_data.sensor_types + tmp_sensor_types
        interval_data.sensor_readings = interval_data.sensor_readings + tmp_sensor_readings
        count = count + 1

    if installed_sensors.raspberry_pi_sense_hat:
        sensor_access = sensor_modules.RaspberryPi_SenseHAT.CreateRPSenseHAT()

        if count > 0:
            interval_data.sensor_types = interval_data.sensor_types + ", "
            interval_data.sensor_readings = interval_data.sensor_readings + ", "

        tmp_sensor_types = "EnvironmentTemp, Pressure, Humidity"

        temperature = sensor_access.temperature()
        pressure = sensor_access.pressure()
        humidity = sensor_access.humidity()

        tmp_sensor_readings = "'" + str(temperature) + "', '" + \
                              str(pressure) + "', '" + \
                              str(humidity) + "'"

        led_message = "SenseHAT " + str(int(temperature)) + "C " + str(pressure) + "hPa " + str(int(humidity)) + "%RH"
        sensor_access.display_led_message(led_message)

        interval_data.sensor_types = interval_data.sensor_types + tmp_sensor_types
        interval_data.sensor_readings = interval_data.sensor_readings + tmp_sensor_readings
        count = count + 1

    if installed_sensors.pimoroni_bh1745:
        sensor_access = sensor_modules.Pimoroni_BH1745.CreateBH1745()

        if count > 0:
            interval_data.sensor_types = interval_data.sensor_types + ", "
            interval_data.sensor_readings = interval_data.sensor_readings + ", "

        tmp_sensor_types = "Lumen, Red, Green, Blue"

        rgb_colour = sensor_access.rgb()
        tmp_sensor_readings = "'" + str(sensor_access.lumen()) + "', '" + \
                              str(rgb_colour[0]) + "', '" + \
                              str(rgb_colour[1]) + "', '" + \
                              str(rgb_colour[2]) + "'"

        interval_data.sensor_types = interval_data.sensor_types + tmp_sensor_types
        interval_data.sensor_readings = interval_data.sensor_readings + tmp_sensor_readings
        count = count + 1

    if installed_sensors.pimoroni_bme680:
        sensor_access = sensor_modules.Pimoroni_BME680.CreateBME680()

        if count > 0:
            interval_data.sensor_types = interval_data.sensor_types + ", "
            interval_data.sensor_readings = interval_data.sensor_readings + ", "

        tmp_sensor_types = "EnvironmentTemp, Pressure, Humidity"

        tmp_sensor_readings = "'" + str(sensor_access.temperature()) + "', '" + \
                              str(sensor_access.pressure()) + "', '" + \
                              str(sensor_access.humidity()) + "'"

        interval_data.sensor_types = interval_data.sensor_types + tmp_sensor_types
        interval_data.sensor_readings = interval_data.sensor_readings + tmp_sensor_readings
        count = count + 1

    if installed_sensors.pimoroni_enviro:
        sensor_access = sensor_modules.Pimoroni_Enviro.CreateEnviro()

        if count > 0:
            interval_data.sensor_types = interval_data.sensor_types + ", "
            interval_data.sensor_readings = interval_data.sensor_readings + ", "

        tmp_sensor_types = "EnvironmentTemp, Pressure, Lumen, Red, Green, Blue"

        rgb_colour = sensor_access.rgb()
        tmp_sensor_readings = "'" + str(sensor_access.temperature()) + "', '" + \
                              str(sensor_access.pressure()) + "', '" + \
                              str(sensor_access.lumen()) + "', '" + \
                              str(rgb_colour[0]) + "', '" + \
                              str(rgb_colour[1]) + "', '" + \
                              str(rgb_colour[2]) + "'"

        interval_data.sensor_types = interval_data.sensor_types + tmp_sensor_types
        interval_data.sensor_readings = interval_data.sensor_readings + tmp_sensor_readings

    return interval_data


def get_trigger_sensor_data():
    trigger_data = Operations_DB.CreateTriggerDatabaseData()

    count = 0
    if installed_sensors.linux_system:
        sensor_access = sensor_modules.Linux_OS.CreateLinuxSystem()

        sensor_types = "SensorName, IP"
        sensor_readings = "'" + str(sensor_access.get_hostname()) + "', '" + str(sensor_access.get_ip()) + "'"

        trigger_data.sensor_types = trigger_data.sensor_types + sensor_types
        trigger_data.sensor_readings = trigger_data.sensor_readings + sensor_readings
        count = count + 1

    if installed_sensors.raspberry_pi_sense_hat:
        sensor_access = sensor_modules.RaspberryPi_SenseHAT.CreateRPSenseHAT()

        if count > 0:
            trigger_data.sensor_types = trigger_data.sensor_types + ", "
            trigger_data.sensor_readings = trigger_data.sensor_readings + ", "

        sensor_types = "Acc_X ,Acc_Y ,Acc_Z ,Mag_X ,Mag_Y ,Mag_Z, Gyro_X, Gyro_Y, Gyro_Z"

        trigger_data.acc_x, trigger_data.acc_y, trigger_data.acc_z = sensor_access.accelerometer_xyz()
        trigger_data.mag_x, trigger_data.mag_y, trigger_data.mag_z = sensor_access.magnetometer_xyz()
        trigger_data.gyro_x, trigger_data.gyro_y, trigger_data.gyro_z = sensor_access.gyroscope_xyz()

        sensor_readings = "'" + str(trigger_data.acc_x) + "', '" + \
                          str(trigger_data.acc_y) + "', '" + \
                          str(trigger_data.acc_z) + "', '" + \
                          str(trigger_data.mag_x) + "', '" + \
                          str(trigger_data.mag_y) + "', '" + \
                          str(trigger_data.mag_z) + "', '" + \
                          str(trigger_data.gyro_x) + "', '" + \
                          str(trigger_data.gyro_y) + "', '" + \
                          str(trigger_data.gyro_z) + "'"

        trigger_data.sensor_types = trigger_data.sensor_types + sensor_types
        trigger_data.sensor_readings = trigger_data.sensor_readings + sensor_readings
        count = count + 1

    if installed_sensors.pimoroni_enviro:
        sensor_access = sensor_modules.Pimoroni_Enviro.CreateEnviro()

        if count > 0:
            trigger_data.sensor_types = trigger_data.sensor_types + ", "
            trigger_data.sensor_readings = trigger_data.sensor_readings + ", "

        sensor_types = "Acc_X ,Acc_Y ,Acc_Z ,Mag_X ,Mag_Y ,Mag_Z"

        trigger_data.acc_x, trigger_data.acc_y, trigger_data.acc_z = sensor_access.accelerometer_xyz()
        trigger_data.mag_x, trigger_data.mag_y, trigger_data.mag_z = sensor_access.magnetometer_xyz()

        sensor_readings = "'" + str(trigger_data.acc_x) + "', '" + \
                          str(trigger_data.acc_y) + "', '" + \
                          str(trigger_data.acc_z) + "', '" + \
                          str(trigger_data.mag_x) + "', '" + \
                          str(trigger_data.mag_y) + "', '" + \
                          str(trigger_data.mag_z) + "'"

        trigger_data.sensor_types = trigger_data.sensor_types + sensor_types
        trigger_data.sensor_readings = trigger_data.sensor_readings + sensor_readings
        count = count + 1

    if installed_sensors.pimoroni_lsm303d:
        sensor_access = sensor_modules.Pimoroni_LSM303D.CreateLSM303D()

        if count > 0:
            trigger_data.sensor_types = trigger_data.sensor_types + ", "
            trigger_data.sensor_readings = trigger_data.sensor_readings + ", "

        sensor_types = "Acc_X ,Acc_Y ,Acc_Z ,Mag_X ,Mag_Y ,Mag_Z"

        trigger_data.acc_x, trigger_data.acc_y, trigger_data.acc_z = sensor_access.accelerometer_xyz()
        trigger_data.mag_x, trigger_data.mag_y, trigger_data.mag_z = sensor_access.magnetometer_xyz()

        sensor_readings = "'" + str(trigger_data.acc_x) + "', '" + \
                          str(trigger_data.acc_y) + "', '" + \
                          str(trigger_data.acc_z) + "', '" + \
                          str(trigger_data.mag_x) + "', '" + \
                          str(trigger_data.mag_y) + "', '" + \
                          str(trigger_data.mag_z) + "'"

        trigger_data.sensor_types = trigger_data.sensor_types + sensor_types
        trigger_data.sensor_readings = trigger_data.sensor_readings + sensor_readings

    return trigger_data
