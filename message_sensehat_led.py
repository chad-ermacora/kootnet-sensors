import sys
import sense_hat

sense = sense_hat.SenseHat()


def display_led_message(message):
    try:
        acc_data = sense.get_accelerometer_raw()

        if acc_data['x'] < -0.5:
            sense.set_rotation(90)
        elif acc_data['y'] > 0.5:
            sense.set_rotation(0)
        elif acc_data['y'] < -0.5:
            sense.set_rotation(180)
        else:
            sense.set_rotation(270)

        sense.show_message(str(message), text_colour=(75, 0, 0))
        print("Message Printed to LED Grid: " + message)
    except Exception as error:
        print("error: " + str(error))


display_led_message(str(sys.argv[1]))
