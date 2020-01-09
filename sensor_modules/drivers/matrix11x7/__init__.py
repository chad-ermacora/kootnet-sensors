"""Python library for the Pimoroni 11x7 LED Matrix Breakout."""
import atexit
from . import is31fl3731
from .fonts import font5x7
import numpy

__version__ = '0.0.1'

DISPLAY_WIDTH = width = 11
DISPLAY_HEIGHT = height = 7


class Matrix11x7:
    def __init__(self, i2c_dev=None, i2c_address=0x75):
        """Set up 11x7 Matrix.

        :param i2c_dev: smbus-compatible i2c object
        :param i2c_address: 7-bit i2c address

        """
        self.width = DISPLAY_WIDTH
        self.height = DISPLAY_HEIGHT
        self._clear_on_exit = True
        self._current_frame = 0
        self._font = font5x7
        self._flipx = False
        self._flipy = False
        self._scroll = [0, 0]
        self._rotate = 0
        self._brightness = 1.0
        self._gamma_table = [
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 1, 1,
            1, 1, 1, 1, 1, 2, 2, 2,
            2, 2, 2, 3, 3, 3, 3, 3,
            4, 4, 4, 4, 5, 5, 5, 5,
            6, 6, 6, 7, 7, 7, 8, 8,
            8, 9, 9, 9, 10, 10, 11, 11,
            11, 12, 12, 13, 13, 13, 14, 14,
            15, 15, 16, 16, 17, 17, 18, 18,
            19, 19, 20, 21, 21, 22, 22, 23,
            23, 24, 25, 25, 26, 27, 27, 28,
            29, 29, 30, 31, 31, 32, 33, 34,
            34, 35, 36, 37, 37, 38, 39, 40,
            40, 41, 42, 43, 44, 45, 46, 46,
            47, 48, 49, 50, 51, 52, 53, 54,
            55, 56, 57, 58, 59, 60, 61, 62,
            63, 64, 65, 66, 67, 68, 69, 70,
            71, 72, 73, 74, 76, 77, 78, 79,
            80, 81, 83, 84, 85, 86, 88, 89,
            90, 91, 93, 94, 95, 96, 98, 99,
            100, 102, 103, 104, 106, 107, 109, 110,
            111, 113, 114, 116, 117, 119, 120, 121,
            123, 124, 126, 128, 129, 131, 132, 134,
            135, 137, 138, 140, 142, 143, 145, 146,
            148, 150, 151, 153, 155, 157, 158, 160,
            162, 163, 165, 167, 169, 170, 172, 174,
            176, 178, 179, 181, 183, 185, 187, 189,
            191, 193, 194, 196, 198, 200, 202, 204,
            206, 208, 210, 212, 214, 216, 218, 220,
            222, 224, 227, 229, 231, 233, 235, 237,
            239, 241, 244, 246, 248, 250, 252, 255]

        self.display = None
        self.buf = None

        self.display = is31fl3731.IS31FL3731(
            i2c=i2c_dev,
            address=i2c_address)

        enable_pattern = [
            # Matrix A   Matrix B
            0b01111111, 0b01111111,
            0b01111111, 0b01111111,
            0b01111111, 0b01111111,
            0b01111111, 0b01111111,
            0b01111111, 0b01111111,
            0b01111111, 0b00000000,
            0b00000000, 0b00000000,
            0b00000000, 0b00000000,
            0b00000000, 0b00000000,
        ]

        for frame in range(is31fl3731._NUM_FRAMES):
            self.display.enable_leds(frame, enable_pattern)

        self.clear()

        atexit.register(self._exit)

    def set_clear_on_exit(self, value=True):
        """Set whether 11x7 Matrix should be cleared upon exit.

        By default, 11x7 Matrix will turn off the pixel on exit, but calling::

            matrix11x7.set_clear_on_exit(False)

        Will ensure that it does not.

        :param value: True or False (default True)

        """
        global _clear_on_exit
        _clear_on_exit = value

    def set_pixel(self, x, y, brightness):
        """Set a single pixel in the buffer.

        :param x: Position of pixel from left of buffer
        :param y: Position of pixel from top of buffer
        :param brightness: Intensity of the pixel, from 0.0 to 1.0

        """
        if brightness > 1.0 or brightness < 0:
            raise ValueError('Value {} out of range. Brightness must be between 0 and 1'.format(brightness))

        if x < 0 or y < 0:
            raise ValueError('Pixel coordinates x and y must be positive integers.')

        try:
            self.buf[x][y] = brightness
        except IndexError:
            self.buf = self.grow_buffer(x + 1, y + 1)
            self.buf[x][y] = brightness

    def pixel(self, x, y, brightness):
        """Set a single pixel in the buffer.

        :param x: Position of pixel from left of buffer
        :param y: Position of pixel from top of buffer
        :param brightness: Intensity of the pixel, from 0.0 to 1.0

        """
        self.set_pixel(x, y, brightness)

    def grow_buffer(self, x, y):
        """Grows a copy of the buffer until the new shape fits inside it.

        :param x: Minimum x size
        :param y: Minimum y size

        """
        x_pad = max(0, x - self.buf.shape[0])
        y_pad = max(0, y - self.buf.shape[1])
        return numpy.pad(self.buf, ((0, x_pad), (0, y_pad)), 'constant')

    def get_shape(self):
        """Get the size/shape of the display.

        Returns a tuple containing the width and height of the display, after applying rotation.

        """
        if self._rotate % 2:
            return (self.height, self.width)

        return (self.width, self.height)

    def show(self, before_display=None):
        """Show the buffer contents on the display.

        The buffer is copied, then scrolling, rotation and flip y/x transforms applied before taking an 11x7 slice and displaying.

        """
        self._current_frame = not self._current_frame

        display_width, display_height = self.get_shape()
        display_buffer = self.grow_buffer(display_width, display_height)

        for axis in [0, 1]:
            if not self._scroll[axis] == 0:
                display_buffer = numpy.roll(
                    display_buffer,
                    -self._scroll[axis],
                    axis=axis)

        # Chop a width * height window out of the display buffer
        display_buffer = display_buffer[:display_width, :display_height]

        # Allow the cropped buffer to be modified in-place before it's transformed and displayed
        # This permits static elements to be drawn over the top of a scrolling buffer
        if callable(before_display):
            display_buffer = before_display(display_buffer)

        if self._flipx:
            display_buffer = numpy.flipud(display_buffer)

        if self._flipy:
            display_buffer = numpy.fliplr(display_buffer)

        if self._rotate:
            display_buffer = numpy.rot90(display_buffer, self._rotate)

        for x in range(width):
            for y in range(height):
                idx = self._pixel_addr(x, height - (y + 1))

                try:
                    value = self._gamma_table[int(display_buffer[x][y] * 255 * self._brightness)]
                except IndexError:
                    value = 0

                self.display.set_pixel(self._current_frame, idx, value)

        self.display.update_frame(self._current_frame)
        self.display.show_frame(self._current_frame)

    def set_graph(self, values, low=None, high=None, brightness=1.0, x=0, y=0, width=None, height=None):
        """Plot a series of values into the display buffer."""
        if width is None:
            width = self.width

        if height is None:
            height = self.height

        if low is None:
            low = min(values)

        if high is None:
            high = max(values)

        self.buf = self.grow_buffer(x + width, y + height)

        span = high - low

        for p_x in range(width):
            try:
                value = values[p_x]
                value -= low
                value /= float(span)
                value *= height * 10.0

                value = min(value, height * 10)
                value = max(value, 0)

                for p_y in range(height):
                    b = brightness
                    if value <= 10:
                        b = (value / 10.0) * brightness

                    self.set_pixel(x + p_x, y + (height - p_y), b)
                    value -= 10
                    if value < 0:
                        value = 0

            except IndexError:
                return

    def set_brightness(self, brightness):
        """Set a global brightness value.

        :param brightness: Brightness value from 0.0 to 1.0

        """
        self._brightness = brightness

    def scroll(self, x=1, y=0):
        """Offset the buffer by x/y pixels.

        11x7 Matrix displays an 11x7 pixel window into the buffer,
        which starts at the left/x offset and wraps around.

        Supplied x and y values are added to the internal scroll offset.

        If called with no arguments, a horizontal right to left scroll by 1 pixel is applied.

        :param x: Number of pixels to scroll on x-axis (default 1)
        :param y: Number of pixels to scroll on y-axis (default 0)

        """
        self._scroll[0] += x
        self._scroll[1] += y

    def scroll_to(self, x=0, y=0):
        """Scroll the buffer to a specific location.

        11x7 Matrix displays an 11x7 pixel window into the buffer
        which starts at the left/x offset and wraps around.

        Supplied x and y values set the internal scroll offset.

        If called with no arguments, the scroll offset is reset to 0, 0

        :param x: Pixel position to scroll to on x-axis (default 0)
        :param y: Pixel position to scroll to on y-axis (default 0)

        """
        self._scroll[0] = x
        self._scroll[1] = y

    def rotate(self, degrees=0):
        """Rotate the buffer 0, 90, 180 or 270 degrees before displaying.

        :param degrees: Amount to rotate, will snap to nearest 90

        """
        self._rotate = int(round(degrees / 90.0))

    def flip(self, x=False, y=False):
        """Flip the buffer horizontally and/or vertically before displaying.

        :param x: Flip horizontally left to right
        :param y: Flip vertically up to down

        """
        self._flipx = x
        self._flipy = y

    def draw_char(self, x, y, char, font=None, brightness=1.0, monospaced=False):
        """Draw a single character to the buffer.

        Returns the x and y coordinates of the bottom-left most corner of the drawn character.

        :param o_x: Offset x - distance of char from left of the buffer.
        :param o_y: Offset y - distance of char from top of the buffer.
        :param char: Char to display- either an integer ordinal or a single character.
        :param font: Font to use, default is to use the one specified with `set_font`
        :param brightness: Brightness of the pixels that comprise the char, from 0.0 to 1.0.
        :param monospaced: Whether to space characters out evenly using `font.width`

        """
        if font is None:
            if self._font is None:
                raise ValueError('You must specify or set a font.')
            font = self._font

        if char in font.data:
            char_map = font.data[char]
        elif type(char) is not int and ord(char) in font.data:
            char_map = font.data[ord(char)]
        else:
            return (x, y)

        for px in range(len(char_map[0])):
            for py in range(len(char_map)):
                pixel = char_map[py][px]
                if pixel:
                    self.set_pixel(
                        x + px,
                        y + py,
                        (pixel / 255.0) * brightness)

        if monospaced:
            px = font.width - 1

        return (x + px, y + font.height)

    def calculate_string_width(self, string, font=None, letter_spacing=1, monospaced=False):
        """Calculate the width of a string.

        :param string: The string to measure
        :param font: Font to use, by default the one specified with `set_font` is used.
        :param letter_spacing: Distance (in pixels) between characters.
        :param monospaced: Whether to space characters out evenly using `font.width`

        """
        width = 0
        for char in string:
            width += self.calculate_char_width(
                char,
                font=font,
                monospaced=monospaced)

            width += 1 + letter_spacing

        return width

    def calculate_char_width(self, char, font=None, monospaced=False):
        """Calculate the width of a single character in the current or specified font.

        :param char: The character to measure
        :param font: Font to use, by default the one specified with `set_font` is used.
        :param monospaced: Whether to space characters out evenly using `font.width`

        """
        if font is None:
            if self._font is None:
                raise ValueError('You must specify or set a font.')
            font = self._font

        if monospaced:
            return font.width - 1

        if char in font.data:
            char_map = font.data[char]
        elif type(char) is not int and ord(char) in font.data:
            char_map = font.data[ord(char)]
        else:
            return 0

        return len(char_map[0]) - 1

    def write_string(self, string, x=0, y=0, font=None, letter_spacing=1, brightness=1.0, monospaced=False, fill_background=False):
        """Write a string to the buffer. Calls draw_char for each character.

        :param string: The string to display.
        :param x: Offset x - distance of string from left of the buffer
        :param y: Offset y - distance of string from right of the buffer
        :param letter_spacing: Distance (in pixels) between characters
        :param font: Font to use, defualt is to use the one specified with `set_font`
        :param brightness: Brightness of the pixels that comprise the text, from 0.0 to 1.0
        :param monospaced: Whether to space characters evenly using `font.width`
        :param fill_background: Not used

        """
        o_x = x

        if font is None:
            if self._font is None:
                raise ValueError('You must specify or set a font.')
            font = self._font

        string_width = self.calculate_string_width(
            string,
            font,
            letter_spacing,
            monospaced)

        self.buf = self.grow_buffer(x + string_width, y + font.height)

        for char in string:
            x, _ = self.draw_char(
                x,
                y,
                char,
                font=font,
                brightness=brightness,
                monospaced=monospaced)

            x += 1 + letter_spacing

        return x - o_x

    def fill(self, brightness, x=0, y=0, width=None, height=None):
        """Fill an area of the display.

        :param brightness: Brightness of pixels.
        :param x: Offset x - distance of area from left of buffer.
        :param y: Offset y - distance of area from top of buffer.
        :param width: Width of area (default is buffer width).
        :param height: Height of area (default is buffer height).

        """
        if width is None:
            width = self.buf.shape[0]

        if height is None:
            height = self.buf.shape[1]

        if (x + width) > self.buf.shape[0] or (y + height) > self.buf.shape[1]:
            self.buf = self.grow_buffer(x + width, y + height)

        # Fill in one operation using a slice
        self.buf[x:x + width, y:y + height] = brightness

    def clear_rect(self, x, y, width, height):
        """Clear a rectangular area.

        :param x: Offset x - distance from left of buffer
        :param y: Offset y - distance from top of buffer
        :param width: Width of area (default is 17)
        :param height: Heigh of area (default is 7)

        """
        self.fill(0, x, y, width, height)

    def clear(self):
        """Clear the buffer.

        You must call `show` after clearing the buffer to update the display.

        """
        self._current_frame = 0
        self._scroll = [0, 0]

        self.buf = numpy.zeros((self.width, self.height))

    def get_buffer_shape(self):
        """Get the size/shape of the internal buffer.

        Returns a tuple containing the width and height of the buffer.

        """
        return self.buf.shape

    def _pixel_addr(self, x, y):
        """Translate an x,y coordinate to a pixel index."""
        mapping = [
            6, 22, 38, 54, 70, 86, 14, 30, 46, 62, 78,
            5, 21, 37, 53, 69, 85, 13, 29, 45, 61, 77,
            4, 20, 36, 52, 68, 84, 12, 28, 44, 60, 76,
            3, 19, 35, 51, 67, 83, 11, 27, 43, 59, 75,
            2, 18, 34, 50, 66, 82, 10, 26, 42, 58, 74,
            1, 17, 33, 49, 65, 81, 9, 25, 41, 57, 73,
            0, 16, 32, 48, 64, 80, 8, 24, 40, 56, 72
        ]

        y = self.height - 1 - y
        return mapping[(y * self.width) + x]

    def set_font(self, font):
        """Change the default font.

        :param font: font object to use

        """
        self._font = font

    def _exit(self):
        self.clear()
        self.show()
