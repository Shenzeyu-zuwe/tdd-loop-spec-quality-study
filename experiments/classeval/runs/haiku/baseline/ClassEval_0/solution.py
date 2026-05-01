import logging
import datetime

class AccessGatewayFilter:
    """
    This class is a filter used for accessing gateway filtering, primarily for authentication and access log recording.
    """

    def __init__(self):
        self.current_user = None
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def filter(self, request):
        """
        Filter the incoming request based on certain rules and conditions.
        :param request: dict, the incoming request details
        :return: bool, True if the request is allowed, False otherwise
        """
        request_path = request.get('path', '')
        
        if not self.is_start_with(request_path):
            return False
        
        if request_path.startswith('/login'):
            return True
        
        user = self.get_jwt_user(request)
        if user is None:
            return False
        
        user_info = user.copy()
        if 'address' in request:
            user_info['address'] = request['address']
        
        self.set_current_user_info_and_log(user_info)
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
        try:
            auth = request.get('headers', {}).get('Authorization')
            if not auth:
                return None
            
            user = auth.get('user')
            jwt_token = auth.get('jwt')
            
            if not user or not jwt_token:
                return None
            
            username = user.get('name')
            if not username:
                return None
            
            expected_jwt = username + str(datetime.date.today())
            
            if jwt_token == expected_jwt:
                return user
            return None
        except:
            return None

    def set_current_user_info_and_log(self, user):
        """
        Set the current user information and log the access.
        :param user: dict, the user information
        :return: None
        """
        self.current_user = user
        username = user.get('name', 'unknown')
        address = user.get('address', 'unknown')
        self.logger.info(f"User {username} accessed from {address}")