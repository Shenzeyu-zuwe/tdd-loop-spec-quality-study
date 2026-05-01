class ArgumentParser:
    def __init__(self):
        self.arguments = {}
        self.required = set()
        self.types = {}

    def parse_arguments(self, command_string):
        tokens = command_string.split()
        tokens = tokens[1:]
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if token.startswith('--'):
                if '=' in token:
                    arg, value = token[2:].split('=', 1)
                else:
                    arg = token[2:]
                    if i + 1 < len(tokens) and not tokens[i + 1].startswith('-'):
                        value = tokens[i + 1]
                        i += 1
                    else:
                        value = None
            elif token.startswith('-'):
                arg = token[1:]
                if i + 1 < len(tokens) and not tokens[i + 1].startswith('-'):
                    value = tokens[i + 1]
                    i += 1
                else:
                    value = None
            else:
                i += 1
                continue
            
            if value is None:
                arg_type = self.types.get(arg, str)
                if arg_type == bool:
                    self.arguments[arg] = True
            else:
                converted_value = self._convert_type(arg, value)
                self.arguments[arg] = converted_value
            
            i += 1
        
        missing = self.required - set(self.arguments.keys())
        if missing:
            return (False, missing)
        else:
            return (True, None)

    def get_argument(self, key):
        return self.arguments.get(key)

    def add_argument(self, arg, required=False, arg_type=str):
        if required:
            self.required.add(arg)
        self.types[arg] = arg_type

    def _convert_type(self, arg, value):
        if arg not in self.types:
            return value
        
        arg_type = self.types[arg]
        
        try:
            if arg_type == bool:
                return bool(value)
            else:
                return arg_type(value)
        except Exception:
            return value