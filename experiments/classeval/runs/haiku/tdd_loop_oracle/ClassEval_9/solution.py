

class BigNumCalculator:
    """
    This is a class that implements big number calculations, including adding, subtracting and multiplying.
    """

    @staticmethod
    def add(num1, num2):
        """
        Adds two big numbers.
        :param num1: The first number to add,str.
        :param num2: The second number to add,str.
        :return: The sum of the two numbers,str.
        >>> bigNum = BigNumCalculator()
        >>> bigNum.add("12345678901234567890", "98765432109876543210")
        '111111111011111111100'

        """
        digits1 = list(reversed(num1))
        digits2 = list(reversed(num2))
        result = []
        carry = 0
        i = 0

        while i < len(digits1) or i < len(digits2) or carry:
            d1 = int(digits1[i]) if i < len(digits1) else 0
            d2 = int(digits2[i]) if i < len(digits2) else 0
            total = d1 + d2 + carry
            result.append(str(total % 10))
            carry = total // 10
            i += 1

        return ''.join(reversed(result))

    @staticmethod
    def subtract(num1, num2):
        """
        Subtracts two big numbers.
        :param num1: The first number to subtract,str.
        :param num2: The second number to subtract,str.
        :return: The difference of the two numbers,str.
        >>> bigNum = BigNumCalculator()
        >>> bigNum.subtract("12345678901234567890", "98765432109876543210")
        '-86419753208641975320'

        """
        # Determine which number is larger
        if len(num1) > len(num2):
            is_negative = False
            larger = num1
            smaller = num2
        elif len(num1) < len(num2):
            is_negative = True
            larger = num2
            smaller = num1
        else:
            # Same length, compare lexicographically
            if num1 >= num2:
                is_negative = False
                larger = num1
                smaller = num2
            else:
                is_negative = True
                larger = num2
                smaller = num1

        # Reverse for easier processing
        digits_larger = list(reversed(larger))
        digits_smaller = list(reversed(smaller))

        result = []
        borrow = 0
        i = 0

        while i < len(digits_larger):
            d1 = int(digits_larger[i])
            d2 = int(digits_smaller[i]) if i < len(digits_smaller) else 0

            diff = d1 - d2 - borrow
            if diff < 0:
                diff += 10
                borrow = 1
            else:
                borrow = 0

            result.append(str(diff))
            i += 1

        # Remove leading zeros
        while len(result) > 1 and result[-1] == '0':
            result.pop()

        result_str = ''.join(reversed(result))

        if is_negative and result_str != '0':
            result_str = '-' + result_str

        return result_str

    @staticmethod
    def multiply(num1, num2):
        """
        Multiplies two big numbers.
        :param num1: The first number to multiply,str.
        :param num2: The second number to multiply,str.
        :return: The product of the two numbers,str.
        >>> bigNum = BigNumCalculator()
        >>> bigNum.multiply("12345678901234567890", "98765432109876543210")
        '1219326311370217952237463801111263526900'

        """
        result = int(num1) * int(num2)
        return str(result)
