def get_osm_sensor_template():
    """ Returns a list of dictionary sensor types of the Pimoroni BH1745 Hat for Open Sense Map registration. """
    return [
        {
            "title": "Lumen",
            "unit": "lm",
            "sensorType": "PimoroniBH1745",
            "icon": "osem-brightness"
        }, {
            "title": "Red",
            "unit": "lm",
            "sensorType": "PimoroniBH1745",
            "icon": "osem-brightness"
        }, {
            "title": "Green",
            "unit": "lm",
            "sensorType": "PimoroniBH1745",
            "icon": "osem-brightness"
        }, {
            "title": "Blue",
            "unit": "lm",
            "sensorType": "PimoroniBH1745",
            "icon": "osem-brightness"
        }
    ]
