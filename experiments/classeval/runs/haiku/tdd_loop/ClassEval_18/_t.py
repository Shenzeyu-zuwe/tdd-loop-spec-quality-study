import sys
sys.path.insert(0, '.')

from solution import CamelCaseMap
camelize_map = CamelCaseMap()
camelize_map['first_name'] = 'John'
camelize_map['last_name'] = 'Doe'
camelize_map['age'] = 30
print(camelize_map.__iter__())
