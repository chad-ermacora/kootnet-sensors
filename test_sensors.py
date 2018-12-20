from operations_modules import operations_config
from operations_modules import operations_sensors
import sensor_modules.raspberry_pi_sensehat

installed_sensors = operations_config.get_installed_sensors()
current_config = operations_config.get_installed_config()

interval_data = operations_sensors.get_interval_sensor_readings()
interval_data.sensor_types = interval_data.sensor_types.split(",")
interval_data.sensor_readings = interval_data.sensor_readings.split(",")

trigger_data = operations_sensors.get_trigger_sensor_readings()
trigger_data.sensor_types = trigger_data.sensor_types.split(",")
trigger_data.sensor_readings = trigger_data.sensor_readings.split(",")
trigger_data.sensor_types = trigger_data.sensor_types[3:]
trigger_data.sensor_readings = trigger_data.sensor_readings[3:]

current_config.custom_temperature_offset = operations_config.get_sensor_temperature_offset()

print("*** Configuration Print || 0 = Disabled | 1 = Enabled ***\n" +
      "Record to SQL: " + str(current_config.write_to_db) +
      "  ||  Enable Custom Variances: " + str(current_config.enable_custom) +
      "\nCustom Temp Offset Enabled: " + str(current_config.enable_custom_temp) +
      " || Current Offset: " + str(current_config.custom_temperature_offset))
print("Interval Delay in Sec: " + str(current_config.sleep_duration_interval) +
      " || Trigger Delay in Sec: " + str(current_config.sleep_duration_trigger))
print("Variances - Acc: " + str(current_config.acc_variance) +
      " || Mag: " + str(current_config.mag_variance) +
      " || Gyro: " + str(current_config.gyro_variance))
print("\n*** Sensor Data test ***")
str_message = ""
count = 0
while count < len(interval_data.sensor_types):
    str_message = str_message + \
                  str(interval_data.sensor_types[count]) + ": " + \
                  str(interval_data.sensor_readings[count] + " | ")

    if count is 1 or count is 4 or count is 6 or count == len(interval_data.sensor_types) - 1:
        print(str_message)
        str_message = ""
    count = count + 1

count = 0
while count < len(trigger_data.sensor_types):
    try:
        trigger_data.sensor_readings[count] = trigger_data.sensor_readings[count].replace("'", "")
        trigger_data.sensor_readings[count] = trigger_data.sensor_readings[count].strip()
        trigger_data.sensor_readings[count] = str(round(float(trigger_data.sensor_readings[count]), 1))
    except Exception as error:
        print(str(error))

    str_message = str_message + trigger_data.sensor_types[count] + ": " + trigger_data.sensor_readings[count] + " | "

    if count is 2 or count is 5 or count is 8 or count == len(trigger_data.sensor_types) - 1:
        print(str_message)
        str_message = ""
    count = count + 1

if installed_sensors.raspberry_pi_sense_hat:
    print("\nShowing SenseHAT Temperature on LED's, Please Wait ...")
    sensor_access = sensor_modules.raspberry_pi_sensehat.CreateRPSenseHAT()
    sensor_access.display_led_message(str(round(sensor_access.temperature(), 2)) + "c")

print("\nTesting Complete")
