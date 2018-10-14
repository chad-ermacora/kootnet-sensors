import operations_sensors
import operations_config

print("*** Configuration Print ***")
operations_config.print_config_to_screen(operations_config.get_installed_config())
print("\n*** Interval Sensor Data test ***")
operations_sensors.print_sensor_readings_to_screen(operations_sensors.get_interval_sensor_readings())
print("\n\n*** Trigger Sensor Data test ***")
operations_sensors.print_sensor_readings_to_screen(operations_sensors.get_trigger_sensor_readings())
