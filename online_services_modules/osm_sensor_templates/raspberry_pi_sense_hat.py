def get_osm_sensor_template():
    """ Returns a list of dictionary sensor types of the Raspberry Pi Sense Hat for Open Sense Map registration. """
    return [
        {
            "title": "Temperature",
            "unit": "°C",
            "sensorType": "RPiSenseHAT",
            "icon": "osem-thermometer"
        }, {
            "title": "Pressure",
            "unit": "hPa",
            "sensorType": "RPiSenseHAT",
            "icon": "osem-barometer"
        }, {
            "title": "Humidity",
            "unit": "%RH",
            "sensorType": "RPiSenseHAT",
            "icon": "osem-humidity"
        }
    ]
