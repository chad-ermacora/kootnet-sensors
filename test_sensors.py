import operations_sensors
import operations_config
import sensor_modules.RaspberryPi_SenseHAT

installed_sensors = operations_config.get_installed_sensors()
config = operations_config.get_installed_config()

interval_data = operations_sensors.get_interval_sensor_readings()
interval_data.sensor_types = interval_data.sensor_types.split(",")
interval_data.sensor_readings = interval_data.sensor_readings.split(",")

trigger_data = operations_sensors.get_trigger_sensor_readings()
trigger_data.sensor_types = trigger_data.sensor_types.split(",")
trigger_data.sensor_readings = trigger_data.sensor_readings.split(",")

print("*** Configuration Print || 0 = Disabled | 1 = Enabled ***\n")
print("Record to SQL Database: " + str(config.write_to_db) + "  ||  Enable Custom Variances: " + str(
    config.enable_custom))
print("Seconds between Interval Recordings: " + str(config.sleep_duration_interval))
print("Seconds between Trigger Checks: " + str(config.sleep_duration_trigger))
print("Variances - Acc: " + str(config.acc_variance) +
      " || Mag: " + str(config.mag_variance) +
      " || Gyro: " + str(config.gyro_variance))

print("\n*** Interval Sensor Data test ***")
str_message = ""
count = 0
while count < len(interval_data.sensor_types):
    str_message = str_message + \
                  str(interval_data.sensor_types[count]) + ": " + \
                  str(interval_data.sensor_readings[count] + " | ")

    if count is 2 or count is 5 or count == len(interval_data.sensor_types) - 1:
        print(str_message)
        str_message = ""
    count = count + 1

print("\n*** Trigger Sensor Data test ***")
count = 0
while count < len(trigger_data.sensor_types):
    str_message = str_message + \
                  str(trigger_data.sensor_types[count]) + ": " + \
                  str(trigger_data.sensor_readings[count] + " | ")

    if count is 1 or count is 4 or count is 7 or count is 10 or count == len(trigger_data.sensor_types) - 1:
        print(str_message)
        str_message = ""
    count = count + 1

if installed_sensors.raspberry_pi_sense_hat:
    print("\nShowing SenseHAT Temperature on LED's, Please Wait ...")
    sensor_access = sensor_modules.RaspberryPi_SenseHAT.CreateRPSenseHAT()
    sensor_access.display_led_message("Temp: " + str(round(sensor_access.temperature(), 2)) + "C")

print("\nTesting Complete")
