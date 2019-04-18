from operations_modules import configuration_main
from operations_modules import sensors
from sensor_modules import raspberry_pi_sensehat


interval_data = sensors.get_interval_sensor_readings()
interval_data.sensor_types = interval_data.sensor_types.split(",")
interval_data.sensor_readings = interval_data.sensor_readings.split(",")

configuration_main.current_config.custom_temperature_offset = configuration_main.current_config.temperature_offset

print("*** Configuration Print || 0 = Disabled | 1 = Enabled ***\n" +
      "Enable Debug Logging: " + str(configuration_main.current_config.enable_debug_logging) +
      "  ||  Record Interval Sensors to SQL Database: " + str(configuration_main.current_config.enable_interval_recording) +
      "\n  Record Trigger Sensors to SQL Database: " + str(configuration_main.current_config.enable_trigger_recording) +
      "\n  Seconds between Interval recordings: " + str(configuration_main.current_config.sleep_duration_interval))
print("\n  Enable Custom Temperature Offset: " + str(configuration_main.current_config.enable_custom_temp) +
      " || Current Temperature Offset: " + str(configuration_main.current_config.temperature_offset))
print("\n*** Sensor Data test ***")
str_message = ""
count = 0
while count < len(interval_data.sensor_types):
    str_message = str_message + \
                  str(interval_data.sensor_types[count]) + ": " + \
                  str(interval_data.sensor_readings[count] + " | ")

    if count is 1 or count is 4 or count is 6 or count is 8 or count is 11 or count is 14 or count == len(
            interval_data.sensor_types) - 1:
        print(str_message)
        str_message = ""
    count = count + 1

count = 0

if configuration_main.installed_sensors.raspberry_pi_sense_hat:
    print("\nShowing SenseHAT Temperature on LED's, Please Wait ...")
    sensor_access = raspberry_pi_sensehat.CreateRPSenseHAT()
    sensor_access.display_led_message(str(round(sensor_access.temperature(), 2)) + "c")

print("\nTesting Complete")
