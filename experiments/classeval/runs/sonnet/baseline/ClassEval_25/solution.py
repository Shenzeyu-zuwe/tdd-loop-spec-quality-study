import json

class CookiesUtil:
    def __init__(self, cookies_file):
        self.cookies_file = cookies_file
        self.cookies = None

    def get_cookies(self, reponse):
        self.cookies = reponse.get('cookies', {})
        self._save_cookies()

    def load_cookies(self):
        try:
            with open(self.cookies_file, 'r') as f:
                self.cookies = json.load(f)
            return self.cookies
        except:
            return {}

    def _save_cookies(self):
        try:
            with open(self.cookies_file, 'w') as f:
                json.dump(self.cookies, f)
            return True
        except:
            return False