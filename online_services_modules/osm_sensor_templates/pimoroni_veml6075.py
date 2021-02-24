def get_osm_sensor_template():
    """ Returns a list of dictionary sensor types of the Pimoroni VEML6075 for Open Sense Map registration. """
    return [
        {
            "title": "UltraVioletIndex",
            "unit": "UV",
            "sensorType": "PimoroniVEML6075",
            "icon": "osem-brightness"
        }, {
            "title": "UltraVioletA",
            "unit": "UVA",
            "sensorType": "PimoroniVEML6075",
            "icon": "osem-brightness"
        }, {
            "title": "UltraVioletB",
            "unit": "UVB",
            "sensorType": "PimoroniVEML6075",
            "icon": "osem-brightness"
        }
    ]
