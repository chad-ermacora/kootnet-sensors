import Operations_Sensors
import Operations_Config

print("*** Configuration Print ***")
Operations_Config.print_config_to_screen(Operations_Config.get_installed_config())
print("\n*** Interval Sensor Data test ***")
Operations_Sensors.print_sql_command_data_to_screen(Operations_Sensors.get_interval_sensor_readings())
print("\n\n*** Trigger Sensor Data test ***")
Operations_Sensors.print_sql_command_data_to_screen(Operations_Sensors.get_trigger_sensor_data())
