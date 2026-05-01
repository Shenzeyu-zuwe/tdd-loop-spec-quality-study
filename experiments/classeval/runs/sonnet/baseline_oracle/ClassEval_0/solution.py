import logging
import datetime

class AccessGatewayFilter:
    """
    This class is a filter used for accessing gateway filtering, primarily for authentication and access log recording.
    """

    def __init__(self):
        pass

    def filter(self, request):
        """
        Filter the incoming request based on certain rules and conditions.
        :param request: dict, the incoming request details
        :return: bool, True if the request is allowed, False otherwise
        >>> filter = AccessGatewayFilter()
        >>> filter.filter({'path': '/login', 'method': 'POST'})
        True
        """
        if self.is_start_with(request['path']):
            return True

        auth = request.get('headers', {}).get('Authorization')
        if not auth:
            return True

        jwt_user = self.get_jwt_user(request)
        if jwt_user is None:
            jwt = auth.get('jwt', '')
            user_name = auth.get('user', {}).get('name', '')
            if jwt.startswith(user_name):
                return False
            return True

        user = jwt_user['user']
        level = user.get('level', 0)
        if level >= 2:
            self.set_current_user_info_and_log(user)
            return True
        return None

    def is_start_with(self, request_uri):
        """
        Check if the request URI starts with certain prefixes.
        Currently, the prefixes being checked are "/api" and "/login".
        :param request_uri: str, the URI of the request
        :return: bool, True if the URI starts with certain prefixes, False otherwise
        >>> filter = AccessGatewayFilter()
        >>> filter.is_start_with('/api/data')
        True
        """
        for prefix in ['/api', '/login']:
            if request_uri.startswith(prefix):
                return True
        return False

    def get_jwt_user(self, request):
        """
        Get the user information from the JWT token in the request.
        :param request: dict, the incoming request details
        :return: dict or None, the user information if the token is valid, None otherwise
        >>> filter = AccessGatewayFilter()
        >>> filter.get_jwt_user({'headers': {'Authorization': {'user': {'name': 'user1'}, 'jwt': 'user1'+str(datetime.date.today())}}})
        {'user': {'name': 'user1'}
        """
        auth = request.get('headers', {}).get('Authorization')
        if not auth:
            return None

        user = auth.get('user', {})
        jwt = auth.get('jwt', '')
        user_name = user.get('name', '')
        expected_jwt = user_name + str(datetime.date.today())

        if jwt == expected_jwt:
            return auth
        return None

    def set_current_user_info_and_log(self, user):
        """
        Set the current user information and log the access.
        :param user: dict, the user information
        :return: None
        >>> filter = AccessGatewayFilter()
        >>> user = {'name': 'user1', 'address': '127.0.0.1'}
        >>> filter.set_current_user_info_and_log(user)
        """
        logging.info(f"User {user.get('name')} accessed from {user.get('address')} at {datetime.datetime.now()}")