def get_osm_sensor_template():
    """ Returns a list of dictionary sensor types of the Pimoroni Enviro for Open Sense Map registration. """
    return [
        {
            "title": "Temperature",
            "unit": "°C",
            "sensorType": "PimoroniEnviroPHAT",
            "icon": "osem-thermometer"
        }, {
            "title": "Pressure",
            "unit": "hPa",
            "sensorType": "PimoroniEnviroPHAT",
            "icon": "osem-barometer"
        }, {
            "title": "Lumen",
            "unit": "lm",
            "sensorType": "PimoroniEnviroPHAT",
            "icon": "osem-brightness"
        }, {
            "title": "Red",
            "unit": "lm",
            "sensorType": "PimoroniEnviroPHAT",
            "icon": "osem-brightness"
        }, {
            "title": "Green",
            "unit": "lm",
            "sensorType": "PimoroniEnviroPHAT",
            "icon": "osem-brightness"
        }, {
            "title": "Blue",
            "unit": "lm",
            "sensorType": "PimoroniEnviroPHAT",
            "icon": "osem-brightness"
        }
    ]
