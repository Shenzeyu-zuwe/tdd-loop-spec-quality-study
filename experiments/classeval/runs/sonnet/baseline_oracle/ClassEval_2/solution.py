class ArgumentParser:
    def __init__(self):
        self.arguments = {}
        self.required = set()
        self.types = {}

    def parse_arguments(self, command_string):
        tokens = command_string.split()
        tokens = tokens[1:]  # skip script name
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.startswith('--'):
                token = token[2:]
            elif token.startswith('-'):
                token = token[1:]
            
            if '=' in token:
                key, value = token.split('=', 1)
                self.arguments[key] = self._convert_type(key, value)
            else:
                if i + 1 < len(tokens) and not tokens[i+1].startswith('-'):
                    self.arguments[token] = self._convert_type(token, tokens[i+1])
                    i += 1
                else:
                    self.arguments[token] = True
            i += 1
        
        missing = self.required - set(self.arguments.keys())
        if missing:
            return (False, missing)
        return (True, None)

    def get_argument(self, key):
        return self.arguments.get(key, None)

    def add_argument(self, arg, required=False, arg_type=str):
        self.types[arg] = arg_type
        if required:
            self.required.add(arg)

    def _convert_type(self, arg, value):
        if arg not in self.types:
            return value
        arg_type = self.types[arg]
        try:
            if arg_type == bool:
                return bool(value)
            return arg_type(value)
        except (ValueError, TypeError):
            return value