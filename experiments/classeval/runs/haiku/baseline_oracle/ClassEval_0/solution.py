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
        """
        path = request.get('path', '')
        
        if self.is_start_with(path):
            return True
        
        if 'headers' not in request or 'Authorization' not in request['headers']:
            return False
        
        auth = request['headers']['Authorization']
        user = auth.get('user')
        
        if not user:
            return False
        
        level = user.get('level', 0)
        if level < 2:
            return None
        
        jwt_user = self.get_jwt_user(request)
        
        if jwt_user is not None:
            return True
        
        jwt = auth.get('jwt', '')
        jwt_username = jwt[:-10] if len(jwt) >= 10 else ''
        
        if jwt_username == user.get('name'):
            return False
        else:
            return True

    def is_start_with(self, request_uri):
        """
        Check if the request URI starts with certain prefixes.
        Currently, the prefixes being checked are "/api" and "/login".
        :param request_uri: str, the URI of the request
        :return: bool, True if the URI starts with certain prefixes, False otherwise
        """
        return request_uri.startswith('/api') or request_uri.startswith('/login')

    def get_jwt_user(self, request):
        """
        Get the user information from the JWT token in the request.
        :param request: dict, the incoming request details
        :return: dict or None, the user information if the token is valid, None otherwise
        """
        if 'headers' not in request or 'Authorization' not in request['headers']:
            return None
        
        auth = request['headers']['Authorization']
        user = auth.get('user')
        jwt = auth.get('jwt')
        
        if not user or not jwt:
            return None
        
        if len(jwt) < 10:
            return None
        
        jwt_date_str = jwt[-10:]
        jwt_username = jwt[:-10]
        
        if jwt_username != user.get('name'):
            return None
        
        try:
            jwt_date = datetime.datetime.strptime(jwt_date_str, '%Y-%m-%d').date()
        except ValueError:
            return None
        
        if jwt_date != datetime.date.today():
            return None
        
        return user

    def set_current_user_info_and_log(self, user):
        """
        Set the current user information and log the access.
        :param user: dict, the user information
        :return: None
        """
        logging.info(f"Current user: {user}")