class Calculator:
    """
    This is a class for a calculator, capable of performing basic arithmetic calculations on numerical expressions using the operators +, -, *, /, and ^ (exponentiation).
    """

    def __init__(self):
        self.operators = {
            '+': lambda x, y: x + y,
            '-': lambda x, y: x - y,
            '*': lambda x, y: x * y,
            '/': lambda x, y: x / y,
            '^': lambda x, y: x ** y
        }

    def calculate(self, expression):
        operand_stack = []
        operator_stack = []
        i = 0
        try:
            while i < len(expression):
                char = expression[i]
                if char.isdigit() or char == '.':
                    j = i
                    while j < len(expression) and (expression[j].isdigit() or expression[j] == '.'):
                        j += 1
                    operand_stack.append(float(expression[i:j]))
                    i = j
                    continue
                elif char in self.operators:
                    while (operator_stack and
                           operator_stack[-1] in self.operators and
                           self.precedence(operator_stack[-1]) >= self.precedence(char)):
                        operand_stack, operator_stack = self.apply_operator(operand_stack, operator_stack)
                    operator_stack.append(char)
                elif char == '(':
                    operator_stack.append(char)
                elif char == ')':
                    while operator_stack and operator_stack[-1] != '(':
                        operand_stack, operator_stack = self.apply_operator(operand_stack, operator_stack)
                    if operator_stack:
                        operator_stack.pop()
                i += 1
            while operator_stack:
                operand_stack, operator_stack = self.apply_operator(operand_stack, operator_stack)
            return operand_stack[0] if operand_stack else None
        except:
            return None

    def precedence(self, operator):
        if operator in ('+', '-'):
            return 1
        elif operator in ('*', '/'):
            return 2
        elif operator == '^':
            return 3
        return 0

    def apply_operator(self, operand_stack, operator_stack):
        operator = operator_stack.pop()
        b = operand_stack.pop()
        a = operand_stack.pop()
        operand_stack.append(self.operators[operator](a, b))
        return operand_stack, operator_stack