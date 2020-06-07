def get_osm_sensor_template():
    """ Returns a list of dictionary sensor types of the Pimoroni BME680 for Open Sense Map registration. """
    return [
        {
            "title": "Temperature",
            "unit": "°C",
            "sensorType": "PimoroniBME680",
            "icon": "osem-thermometer"
        }, {
            "title": "Pressure",
            "unit": "hPa",
            "sensorType": "PimoroniBME680",
            "icon": "osem-barometer"
        }, {
            "title": "Humidity",
            "unit": "%RH",
            "sensorType": "PimoroniBME680",
            "icon": "osem-humidity"
        }, {
            "title": "Gas VOC",
            "unit": "kΩ",
            "sensorType": "PimoroniBME680"
        }
    ]
