import logging
import datetime

class AccessGatewayFilter:
    """
    This class is a filter used for accessing gateway filtering, primarily for authentication and access log recording.
    """

    def __init__(self):
        pass

    def filter(self, request):
        request_uri = request.get('path', '')
        method = request.get('method', '')

        if self.is_start_with(request_uri):
            return True

        jwt_user = self.get_jwt_user(request)
        if jwt_user is None:
            return False

        self.set_current_user_info_and_log(jwt_user.get('user', {}))
        return True

    def is_start_with(self, request_uri):
        prefixes = ['/api', '/login']
        for prefix in prefixes:
            if request_uri.startswith(prefix):
                return True
        return False

    def get_jwt_user(self, request):
        headers = request.get('headers', {})
        auth = headers.get('Authorization', None)
        if auth is None:
            return None

        jwt_token = auth.get('jwt', '')
        user = auth.get('user', {})
        name = user.get('name', '')

        expected_token = name + str(datetime.date.today())
        if jwt_token == expected_token:
            return {'user': user}
        return None

    def set_current_user_info_and_log(self, user):
        host = user.get('address', '')
        name = user.get('name', '')
        logging.info(f"User: {name}, Host: {host}, Time: {datetime.datetime.now()}")