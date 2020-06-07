def get_osm_sensor_template():
    """ Returns a list of dictionary sensor types of the Pimoroni BMP280 for Open Sense Map registration. """
    return [
        {
            "title": "Temperature",
            "unit": "°C",
            "sensorType": "PimoroniBMP280",
            "icon": "osem-thermometer"
        }, {
            "title": "Pressure",
            "unit": "hPa",
            "sensorType": "PimoroniBMP280",
            "icon": "osem-barometer"
        }, {
            "title": "Altitude",
            "unit": "m",
            "sensorType": "PimoroniBMP280"
        }
    ]
