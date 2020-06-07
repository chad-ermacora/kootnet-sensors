def get_osm_sensor_template():
    """ Returns a list of dictionary sensor types of the Pimoroni Enviro+ Hat for Open Sense Map registration. """
    return [
        {
            "title": "Temperature",
            "unit": "°C",
            "sensorType": "PimoroniEnviroPlus",
            "icon": "osem-thermometer"
        }, {
            "title": "Pressure",
            "unit": "hPa",
            "sensorType": "PimoroniEnviroPlus",
            "icon": "osem-barometer"
        }, {
            "title": "Humidity",
            "unit": "%RH",
            "sensorType": "PimoroniEnviroPlus",
            "icon": "osem-humidity"
        }, {
            "title": "Lumen",
            "unit": "lm",
            "sensorType": "PimoroniEnviroPlus",
            "icon": "osem-brightness"
        }, {
            "title": "Oxidised",
            "unit": "kΩ",
            "sensorType": "PimoroniEnviroPlus"
        }, {
            "title": "Reduced",
            "unit": "kΩ",
            "sensorType": "PimoroniEnviroPlus"
        }, {
            "title": "nh3",
            "unit": "kΩ",
            "sensorType": "PimoroniEnviroPlus"
        }
    ]
