class BinaryDataProcessor:
    def __init__(self, binary_string):
        self.binary_string = binary_string
        self.clean_non_binary_chars()

    def clean_non_binary_chars(self):
        self.binary_string = ''.join(c for c in self.binary_string if c in '01')

    def calculate_binary_info(self):
        total = len(self.binary_string)
        ones = self.binary_string.count('1')
        zeroes = self.binary_string.count('0')
        return {'Zeroes': zeroes / total, 'Ones': ones / total, 'Bit length': total}

    def convert_to_ascii(self):
        chars = [self.binary_string[i:i+8] for i in range(0, len(self.binary_string), 8)]
        return ''.join(chr(int(c, 2)) for c in chars if len(c) == 8)

    def convert_to_utf8(self):
        chars = [self.binary_string[i:i+8] for i in range(0, len(self.binary_string), 8)]
        byte_array = bytes(int(c, 2) for c in chars if len(c) == 8)
        return byte_array.decode('utf-8')