

class BinaryDataProcessor:
    """
    This is a class used to process binary data, which includes functions such as clearing non 0 or 1 characters, counting binary string information, and converting to corresponding strings based on different encoding methods.
    """

    def __init__(self, binary_string):
        """
        Initialize the class with a binary string and clean it by removing all non 0 or 1 characters.
        """
        self._binary_string = binary_string
        self.clean_non_binary_chars()

    @property
    def binary_string(self):
        return repr(self._binary_string)

    @binary_string.setter
    def binary_string(self, value):
        self._binary_string = value

    def clean_non_binary_chars(self):
        """
        Clean the binary string by removing all non 0 or 1 characters.
        >>> bdp = BinaryDataProcessor("01101000daf3e4r01100101011011000110110001101111")
        >>> bdp.clean_non_binary_chars()
        >>> bdp.binary_string
        '0110100001100101011011000110110001101111'

        """
        self._binary_string = ''.join(char for char in self._binary_string if char in '01')

    def calculate_binary_info(self):
        """
        Calculate the binary string information, including the percentage of 0 and 1, and the total length of the binary string.
        >>> bdp = BinaryDataProcessor("0110100001100101011011000110110001101111")
        >>> bdp.calculate_binary_info()
        {'Zeroes': 0.475, 'Ones': 0.525, 'Bit length': 40}

        """
        bit_length = len(self._binary_string)
        zeroes_count = self._binary_string.count('0')
        ones_count = self._binary_string.count('1')

        zeroes_percentage = round(zeroes_count / bit_length, 3)
        ones_percentage = round(ones_count / bit_length, 3)

        return {'Zeroes': zeroes_percentage, 'Ones': ones_percentage, 'Bit length': bit_length}

    def convert_to_ascii(self):
        """
        Convert the binary string to ascii string.
        >>> bdp = BinaryDataProcessor("0110100001100101011011000110110001101111")
        >>> bdp.convert_to_ascii()
        'hello'

        """
        result = ''
        for i in range(0, len(self._binary_string), 8):
            byte = self._binary_string[i:i+8]
            result += chr(int(byte, 2))
        return repr(result)

    def convert_to_utf8(self):
        """
        Convert the binary string to utf-8 string.
        >>> bdp = BinaryDataProcessor("0110100001100101011011000110110001101111")
        >>> bdp.convert_to_utf8()
        'hello'

        """
        result = ''
        for i in range(0, len(self._binary_string), 8):
            byte = self._binary_string[i:i+8]
            result += chr(int(byte, 2))
        return repr(result)
