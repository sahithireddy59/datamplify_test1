from django.shortcuts import render
from Datamplify import settings
import requests
from oauth2_provider.models import Application
from oauth2_provider.models import AccessToken,RefreshToken,Application
from authentication.models import UserProfile
import datetime
from pytz import utc
from requests.auth import HTTPBasicAuth
import logging
import time
from requests.exceptions import RequestException, Timeout, ConnectionError
from functools import wraps

logger = logging.getLogger(__name__)

# Circuit breaker to prevent excessive retries when service is down
class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open

    def call(self, func, *args, **kwargs):
        if self.state == 'open':
            # If we're in the recovery timeout period, still fail fast
            if self.last_failure_time and (time.time() - self.last_failure_time) < self.recovery_timeout:
                logger.warning(f"Circuit breaker is open. Skipping call to {func.__name__}")
                raise Exception(f"Circuit breaker is open. Skipping call to {func.__name__}")
            else:
                # Recovery timeout has passed, try again (half-open state)
                self.state = 'half-open'
                self.failure_count = 0
                logger.info(f"Circuit breaker moving to half-open. Attempting call to {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            # Success, reset state
            if self.state == 'half-open':
                self.state = 'closed'
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'open'
                logger.warning(f"Circuit breaker opened after {self.failure_count} failures for {func.__name__}")
            
            raise e

# Global circuit breaker for authentication requests
auth_circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30)



# def get_access_token(username,password):
#     token_url = settings.TOKEN_URL
#     client_id = settings.CLIENT_ID
#     client_secret = settings.CLIENT_SECRET
#     print("Authenticating with:")
#     print("client_id:", client_id)
#     print("client_secret:", client_secret)
#     print("token_url:", token_url)
#     response = requests.post(
#         token_url,
#         data={
#             'grant_type': 'password',
#             'username': username,
#             'password': password
#         },
#         auth=(client_id,client_secret), 
#         headers={'Content-Type': 'application/x-www-form-urlencoded'}
#     )
#     if response.status_code==200:
#         data = {
#             'status':200,
#             'data':response.json()
#         }
#     else:
#         data = {
#             'status':response.status_code,
#             'data':response
#         }
#     return data


def get_access_token(username, password, max_retries=2, initial_timeout=5):
    """
    Get OAuth2 access token with circuit breaker and aggressive fallback mechanisms

    Args:
        username: User username
        password: User password
        max_retries: Maximum number of retry attempts (default: 2)
        initial_timeout: Initial timeout in seconds (default: 5)

    Returns:
        dict: Response containing status, data, and endpoint information
    """
    # Get primary token URL from settings
    primary_token_url = settings.TOKEN_URL
    client_id = settings.CLIENT_ID
    client_secret = settings.CLIENT_SECRET

    # Prepare request data
    data = {
        'grant_type': 'password',
        'username': username,
        'password': password,
        'client_id': client_id,
        'client_secret': client_secret,
        'user': username
    }

    # Prepare headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Define fallback URLs in order of preference
    fallback_urls = [
        'http://127.0.0.1:8000/v1/authentication/o/token/',
        'http://localhost:8000/v1/authentication/o/token/',
        'http://172.16.17.159:8000/v1/authentication/o/token/',  # Alternative production URL
    ]

    # Try all URLs (primary + fallbacks)
    all_urls = [primary_token_url] + fallback_urls

    # Use circuit breaker for the entire authentication process
    try:
        # Try all URLs (primary + fallbacks)
        for url_index, token_url in enumerate(all_urls):
            retry_count = 0
            last_error = None

            logger.info(f"Trying endpoint {url_index + 1}/{len(all_urls)}: {token_url}")

            # For the primary endpoint, use circuit breaker
            if url_index == 0:
                # Wrap the endpoint-specific logic in a circuit breaker
                def attempt_endpoint():
                    nonlocal retry_count, last_error

                    while retry_count <= max_retries:
                        try:
                            # For the first attempt, use a shorter timeout to fail fast
                            if retry_count == 0:
                                timeout = min(initial_timeout, 5)  # Max 5 seconds for first attempt
                            else:
                                # Calculate timeout with exponential backoff for subsequent retries
                                timeout = min(initial_timeout * (2 ** retry_count), 15)  # Cap at 15 seconds

                            logger.info(f"Attempting token request (attempt {retry_count + 1}/{max_retries + 1}) at {token_url}", 
                                       extra={"endpoint": token_url, "timeout": timeout})

                            response = requests.post(token_url, data=data, headers=headers, timeout=timeout)

                            if response.status_code == 200:
                                logger.info(f"Token request successful at {token_url}")
                                return {
                                    'status': 200,
                                    'data': response.json(),
                                    'endpoint': token_url
                                }
                            else:
                                # Handle non-200 status codes
                                try:
                                    content = response.json()
                                except Exception:
                                    content = response.text

                                logger.warning(f"Token request failed with status {response.status_code} at {token_url}", 
                                              extra={"endpoint": token_url, "response": content})

                                # If we get a 401 Unauthorized, don't retry this endpoint
                                if response.status_code == 401:
                                    break

                                return {
                                    'status': response.status_code,
                                    'data': content,
                                    'endpoint': token_url
                                }

                        except Timeout as e:
                            last_error = e
                            logger.warning(f"Token request timed out (attempt {retry_count + 1}/{max_retries + 1}) at {token_url}", 
                                          extra={"endpoint": token_url, "error": str(e)})

                            # If this is our last attempt for this URL, move to the next URL
                            if retry_count == max_retries:
                                logger.info(f"Moving to next endpoint after {max_retries + 1} timeouts at {token_url}")
                                raise e

                            retry_count += 1
                            continue

                        except ConnectionError as e:
                            last_error = e
                            logger.warning(f"Token request connection error (attempt {retry_count + 1}/{max_retries + 1}) at {token_url}", 
                                          extra={"endpoint": token_url, "error": str(e)})

                            # If this is our last attempt for this URL, move to the next URL
                            if retry_count == max_retries:
                                logger.info(f"Moving to next endpoint after {max_retries + 1} connection errors at {token_url}")
                                raise e

                            retry_count += 1
                            continue

                        except RequestException as e:
                            last_error = e
                            logger.warning(f"Token request failed (attempt {retry_count + 1}/{max_retries + 1}) at {token_url}", 
                                          extra={"endpoint": token_url, "error": str(e)})

                            # If this is our last attempt for this URL, move to the next URL
                            if retry_count == max_retries:
                                logger.info(f"Moving to next endpoint after {max_retries + 1} request errors at {token_url}")
                                raise e

                            retry_count += 1
                            continue

                    # If we've exhausted all retries for this URL, raise an exception to move to the next URL
                    raise Exception(f"Exhausted all retries for {token_url}")

                # Execute the endpoint attempt within the circuit breaker
                try:
                    return auth_circuit_breaker.call(attempt_endpoint)
                except Exception as e:
                    # Circuit breaker is open or we've exhausted retries
                    logger.warning(f"Circuit breaker activated or endpoint failed: {str(e)}")
                    # Continue to the next URL
                    continue
            else:
                # For fallback endpoints, don't use circuit breaker but still limit retries
                while retry_count <= max_retries:
                    try:
                        # Use short timeouts for fallback endpoints
                        timeout = min(initial_timeout, 5)  # Max 5 seconds for fallback attempts

                        logger.info(f"Attempting fallback token request (attempt {retry_count + 1}/{max_retries + 1}) at {token_url}", 
                                   extra={"endpoint": token_url, "timeout": timeout})

                        response = requests.post(token_url, data=data, headers=headers, timeout=timeout)

                        if response.status_code == 200:
                            logger.info(f"Fallback token request successful at {token_url}")
                            return {
                                'status': 200,
                                'data': response.json(),
                                'endpoint': token_url
                            }
                        else:
                            # Handle non-200 status codes
                            try:
                                content = response.json()
                            except Exception:
                                content = response.text

                            logger.warning(f"Fallback token request failed with status {response.status_code} at {token_url}", 
                                          extra={"endpoint": token_url, "response": content})

                            # If we get a 401 Unauthorized, don't retry this endpoint
                            if response.status_code == 401:
                                break

                            return {
                                'status': response.status_code,
                                'data': content,
                                'endpoint': token_url
                            }

                    except Timeout as e:
                        last_error = e
                        logger.warning(f"Fallback token request timed out (attempt {retry_count + 1}/{max_retries + 1}) at {token_url}", 
                                      extra={"endpoint": token_url, "error": str(e)})

                        # If this is our last attempt for this URL, move to the next URL
                        if retry_count == max_retries:
                            logger.info(f"Moving to next fallback endpoint after {max_retries + 1} timeouts at {token_url}")
                            break

                        retry_count += 1
                        continue

                    except ConnectionError as e:
                        last_error = e
                        logger.warning(f"Fallback token request connection error (attempt {retry_count + 1}/{max_retries + 1}) at {token_url}", 
                                      extra={"endpoint": token_url, "error": str(e)})

                        # If this is our last attempt for this URL, move to the next URL
                        if retry_count == max_retries:
                            logger.info(f"Moving to next fallback endpoint after {max_retries + 1} connection errors at {token_url}")
                            break

                        retry_count += 1
                        continue

                    except RequestException as e:
                        last_error = e
                        logger.warning(f"Fallback token request failed (attempt {retry_count + 1}/{max_retries + 1}) at {token_url}", 
                                      extra={"endpoint": token_url, "error": str(e)})

                        # If this is our last attempt for this URL, move to the next URL
                        if retry_count == max_retries:
                            logger.info(f"Moving to next fallback endpoint after {max_retries + 1} request errors at {token_url}")
                            break

                        retry_count += 1
                        continue

                # If we've exhausted all retries for this URL, move to the next URL
                logger.warning(f"Exhausted all retries for fallback {token_url}, moving to next endpoint")

    except Exception as e:
        logger.error(f"Unexpected error in authentication process: {str(e)}")

    # If we've tried all URLs and all failed
    logger.error("Token request failed for all endpoints", 
                extra={"primary_endpoint": primary_token_url, "fallback_urls": fallback_urls})
    return {
        'status': 504,
        'data': f'token request failed for all endpoints',
        'endpoint': primary_token_url
    }


def get_access_token_updated(username, password, max_retries=2, initial_timeout=5):
    """
    Get OAuth2 access token with circuit breaker, aggressive fallback mechanisms, and basic auth options

    Args:
        username: User username
        password: User password
        max_retries: Maximum number of retry attempts (default: 2)
        initial_timeout: Initial timeout in seconds (default: 5)

    Returns:
        dict: Response containing status, data, and endpoint information
    """
    # Determine token URL based on database engine
    for name, config in settings.DATABASES.items():
        engine = config.get('ENGINE')
        if engine=='django.db.backends.sqlite3':
            primary_token_url = 'http://127.0.0.1:8000/v1/oauth2/token/'
            break
    else:
        primary_token_url = settings.TOKEN_URL

    client_id = settings.CLIENT_ID
    client_secret = settings.CLIENT_SECRET

    # Prepare request data
    data = {
        'grant_type': 'password',
        'username': username,
        'password': password,
        'client_id': client_id,
        'client_secret': client_secret,
        'user': username
    }

    # Prepare headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Define fallback URLs in order of preference
    fallback_urls = [
        'http://127.0.0.1:8000/v1/oauth2/token/',
        'http://localhost:8000/v1/oauth2/token/',
        'http://172.16.17.159:8000/v1/oauth2/token/',  # Alternative production URL
    ]

    # Try all URLs (primary + fallbacks)
    all_urls = [primary_token_url] + fallback_urls

    # Use circuit breaker for the entire authentication process
    try:
        # Try all URLs (primary + fallbacks)
        for url_index, token_url in enumerate(all_urls):
            retry_count = 0
            last_error = None

            logger.info(f"Trying endpoint {url_index + 1}/{len(all_urls)}: {token_url}")

            # For the primary endpoint, use circuit breaker
            if url_index == 0:
                # Wrap the endpoint-specific logic in a circuit breaker
                def attempt_endpoint():
                    nonlocal retry_count, last_error

                    while retry_count <= max_retries:
                        try:
                            # For the first attempt, use a shorter timeout to fail fast
                            if retry_count == 0:
                                timeout = min(initial_timeout, 5)  # Max 5 seconds for first attempt
                            else:
                                # Calculate timeout with exponential backoff for subsequent retries
                                timeout = min(initial_timeout * (2 ** retry_count), 15)  # Cap at 15 seconds

                            logger.info(f"Attempting token request (attempt {retry_count + 1}/{max_retries + 1}) at {token_url}", 
                                       extra={"endpoint": token_url, "timeout": timeout})

                            response = requests.post(token_url, data=data, headers=headers, timeout=timeout)

                            if response.status_code == 200:
                                logger.info(f"Token request successful at {token_url}")
                                return {
                                    'status': 200,
                                    'data': response.json(),
                                    'endpoint': token_url
                                }
                            else:
                                # Handle non-200 status codes
                                try:
                                    content = response.json()
                                except Exception:
                                    content = response.text

                                logger.warning(f"Token request failed with status {response.status_code} at {token_url}", 
                                              extra={"endpoint": token_url, "response": content})

                                # Try with basic auth if regular request fails
                                try:
                                    basic_auth_response = requests.post(
                                        token_url,
                                        data=data,
                                        headers=headers,
                                        auth=HTTPBasicAuth(client_id, client_secret),
                                        timeout=15  # Shorter timeout for basic auth attempt
                                    )

                                    if basic_auth_response.status_code == 200:
                                        logger.info(f"Token request with basic auth successful at {token_url}")
                                        return {
                                            'status': 200,
                                            'data': basic_auth_response.json(),
                                            'endpoint': token_url
                                        }
                                except Exception as basic_auth_error:
                                    logger.warning(f"Basic auth token request also failed at {token_url}", 
                                                 extra={"endpoint": token_url, "error": str(basic_auth_error)})

                                # If we get a 401 Unauthorized, don't retry this endpoint
                                if response.status_code == 401:
                                    break

                                return {
                                    'status': response.status_code,
                                    'data': content,
                                    'endpoint': token_url
                                }

                        except Timeout as e:
                            last_error = e
                            logger.warning(f"Token request timed out (attempt {retry_count + 1}/{max_retries + 1}) at {token_url}", 
                                          extra={"endpoint": token_url, "error": str(e)})

                            # If this is our last attempt for this URL, move to the next URL
                            if retry_count == max_retries:
                                logger.info(f"Moving to next endpoint after {max_retries + 1} timeouts at {token_url}")
                                raise e

                            retry_count += 1
                            continue

                        except ConnectionError as e:
                            last_error = e
                            logger.warning(f"Token request connection error (attempt {retry_count + 1}/{max_retries + 1}) at {token_url}", 
                                          extra={"endpoint": token_url, "error": str(e)})

                            # If this is our last attempt for this URL, move to the next URL
                            if retry_count == max_retries:
                                logger.info(f"Moving to next endpoint after {max_retries + 1} connection errors at {token_url}")
                                raise e

                            retry_count += 1
                            continue

                        except RequestException as e:
                            last_error = e
                            logger.warning(f"Token request failed (attempt {retry_count + 1}/{max_retries + 1}) at {token_url}", 
                                          extra={"endpoint": token_url, "error": str(e)})

                            # If this is our last attempt for this URL, move to the next URL
                            if retry_count == max_retries:
                                logger.info(f"Moving to next endpoint after {max_retries + 1} request errors at {token_url}")
                                raise e

                            retry_count += 1
                            continue

                    # If we've exhausted all retries for this URL, raise an exception to move to the next URL
                    raise Exception(f"Exhausted all retries for {token_url}")

                # Execute the endpoint attempt within the circuit breaker
                try:
                    return auth_circuit_breaker.call(attempt_endpoint)
                except Exception as e:
                    # Circuit breaker is open or we've exhausted retries
                    logger.warning(f"Circuit breaker activated or endpoint failed: {str(e)}")
                    # Continue to the next URL
                    continue
            else:
                # For fallback endpoints, don't use circuit breaker but still limit retries
                while retry_count <= max_retries:
                    try:
                        # Use short timeouts for fallback endpoints
                        timeout = min(initial_timeout, 5)  # Max 5 seconds for fallback attempts

                        logger.info(f"Attempting fallback token request (attempt {retry_count + 1}/{max_retries + 1}) at {token_url}", 
                                   extra={"endpoint": token_url, "timeout": timeout})

                        response = requests.post(token_url, data=data, headers=headers, timeout=timeout)

                        if response.status_code == 200:
                            logger.info(f"Fallback token request successful at {token_url}")
                            return {
                                'status': 200,
                                'data': response.json(),
                                'endpoint': token_url
                            }
                        else:
                            # Handle non-200 status codes
                            try:
                                content = response.json()
                            except Exception:
                                content = response.text

                            logger.warning(f"Fallback token request failed with status {response.status_code} at {token_url}", 
                                          extra={"endpoint": token_url, "response": content})

                            # Try with basic auth if regular request fails
                            try:
                                basic_auth_response = requests.post(
                                    token_url,
                                    data=data,
                                    headers=headers,
                                    auth=HTTPBasicAuth(client_id, client_secret),
                                    timeout=5  # Short timeout for basic auth attempt
                                )

                                if basic_auth_response.status_code == 200:
                                    logger.info(f"Fallback token request with basic auth successful at {token_url}")
                                    return {
                                        'status': 200,
                                        'data': basic_auth_response.json(),
                                        'endpoint': token_url
                                    }
                            except Exception as basic_auth_error:
                                logger.warning(f"Basic auth fallback token request also failed at {token_url}", 
                                             extra={"endpoint": token_url, "error": str(basic_auth_error)})

                            # If we get a 401 Unauthorized, don't retry this endpoint
                            if response.status_code == 401:
                                break

                            return {
                                'status': response.status_code,
                                'data': content,
                                'endpoint': token_url
                            }

                    except Timeout as e:
                        last_error = e
                        logger.warning(f"Fallback token request timed out (attempt {retry_count + 1}/{max_retries + 1}) at {token_url}", 
                                      extra={"endpoint": token_url, "error": str(e)})

                        # If this is our last attempt for this URL, move to the next URL
                        if retry_count == max_retries:
                            logger.info(f"Moving to next endpoint after {max_retries + 1} timeouts at {token_url}")
                            break

                        retry_count += 1
                        continue

                    except ConnectionError as e:
                        last_error = e
                        logger.warning(f"Fallback token request connection error (attempt {retry_count + 1}/{max_retries + 1}) at {token_url}", 
                                      extra={"endpoint": token_url, "error": str(e)})

                        # If this is our last attempt for this URL, move to the next URL
                        if retry_count == max_retries:
                            logger.info(f"Moving to next endpoint after {max_retries + 1} connection errors at {token_url}")
                            break

                        retry_count += 1
                        continue

                    except RequestException as e:
                        last_error = e
                        logger.warning(f"Fallback token request failed (attempt {retry_count + 1}/{max_retries + 1}) at {token_url}", 
                                      extra={"endpoint": token_url, "error": str(e)})

                        # If this is our last attempt for this URL, move to the next URL
                        if retry_count == max_retries:
                            logger.info(f"Moving to next endpoint after {max_retries + 1} request errors at {token_url}")
                            break

                        retry_count += 1
                        continue

        # If we've exhausted all retries for this URL, move to the next URL
        logger.warning(f"Exhausted all retries for {token_url}, moving to next endpoint")

    except Exception as e:
        # Handle any unexpected errors from the overall authentication process
        logger.error(f"Unexpected error in authentication process: {str(e)}")
        return {
            'status': 500,
            'data': f'unexpected error: {str(e)}',
            'endpoint': primary_token_url
        }

    # If we've tried all URLs and all failed
    logger.error("Token request failed for all endpoints", 
                extra={"primary_endpoint": primary_token_url, "fallback_urls": fallback_urls})
    return {
        'status': 504,
        'data': f'token request failed for all endpoints',
        'endpoint': primary_token_url
    }


def generate_access_from_refresh(refresh_token, max_retries=2, initial_timeout=5):
    """
    Generate a new access token from a refresh token with circuit breaker and aggressive fallback mechanisms

    Args:
        refresh_token: The refresh token to use for generating a new access token
        max_retries: Maximum number of retry attempts (default: 2)
        initial_timeout: Initial timeout in seconds (default: 5)

    Returns:
        dict: Response containing status, data, and endpoint information
    """
    # Get primary token URL from settings
    primary_token_url = settings.TOKEN_URL
    client_id = settings.CLIENT_ID
    client_secret = settings.CLIENT_SECRET

    # Prepare request data
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret,
    }

    # Prepare headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Define fallback URLs in order of preference
    fallback_urls = [
        'http://127.0.0.1:8000/v1/oauth2/token/',
        'http://localhost:8000/v1/oauth2/token/',
        'http://172.16.17.159:8000/v1/oauth2/token/',  # Alternative production URL
    ]

    # Try all URLs (primary + fallbacks)
    all_urls = [primary_token_url] + fallback_urls

    # Use circuit breaker for the entire refresh token process
    try:
        # Try all URLs (primary + fallbacks)
        for url_index, token_url in enumerate(all_urls):
            retry_count = 0
            last_error = None

            logger.info(f"Trying refresh endpoint {url_index + 1}/{len(all_urls)}: {token_url}")

            # For the primary endpoint, use circuit breaker
            if url_index == 0:
                # Wrap the endpoint-specific logic in a circuit breaker
                def attempt_endpoint():
                    nonlocal retry_count, last_error

                    while retry_count <= max_retries:
                        try:
                            # For the first attempt, use a shorter timeout to fail fast
                            if retry_count == 0:
                                timeout = min(initial_timeout, 5)  # Max 5 seconds for first attempt
                            else:
                                # Calculate timeout with exponential backoff for subsequent retries
                                timeout = min(initial_timeout * (2 ** retry_count), 15)  # Cap at 15 seconds

                            logger.info(f"Attempting refresh token request (attempt {retry_count + 1}/{max_retries + 1}) at {token_url}", 
                                       extra={"endpoint": token_url, "timeout": timeout})

                            response = requests.post(token_url, data=data, headers=headers, timeout=timeout)

                            if response.status_code == 200:
                                logger.info(f"Refresh token request successful at {token_url}")
                                return {
                                    'status': 200,
                                    'data': response.json(),
                                    'endpoint': token_url
                                }
                            else:
                                # Handle non-200 status codes
                                try:
                                    content = response.json()
                                except Exception:
                                    content = response.text

                                logger.warning(f"Refresh token request failed with status {response.status_code} at {token_url}", 
                                              extra={"endpoint": token_url, "response": content})

                                # If we get a 401 Unauthorized, don't retry this endpoint
                                if response.status_code == 401:
                                    break

                                return {
                                    'status': response.status_code,
                                    'data': content,
                                    'endpoint': token_url
                                }

                        except Timeout as e:
                            last_error = e
                            logger.warning(f"Refresh token request timed out (attempt {retry_count + 1}/{max_retries + 1}) at {token_url}", 
                                          extra={"endpoint": token_url, "error": str(e)})

                            # If this is our last attempt for this URL, move to the next URL
                            if retry_count == max_retries:
                                logger.info(f"Moving to next endpoint after {max_retries + 1} timeouts at {token_url}")
                                raise e

                            retry_count += 1
                            continue

                        except ConnectionError as e:
                            last_error = e
                            logger.warning(f"Refresh token request connection error (attempt {retry_count + 1}/{max_retries + 1}) at {token_url}", 
                                          extra={"endpoint": token_url, "error": str(e)})

                            # If this is our last attempt for this URL, move to the next URL
                            if retry_count == max_retries:
                                logger.info(f"Moving to next endpoint after {max_retries + 1} connection errors at {token_url}")
                                raise e

                            retry_count += 1
                            continue

                        except RequestException as e:
                            last_error = e
                            logger.warning(f"Refresh token request failed (attempt {retry_count + 1}/{max_retries + 1}) at {token_url}", 
                                          extra={"endpoint": token_url, "error": str(e)})

                            # If this is our last attempt for this URL, move to the next URL
                            if retry_count == max_retries:
                                logger.info(f"Moving to next endpoint after {max_retries + 1} request errors at {token_url}")
                                raise e

                            retry_count += 1
                            continue

                    # If we've exhausted all retries for this URL, raise an exception to move to the next URL
                    raise Exception(f"Exhausted all retries for {token_url}")

                # Execute the endpoint attempt within the circuit breaker
                try:
                    return auth_circuit_breaker.call(attempt_endpoint)
                except Exception as e:
                    # Circuit breaker is open or we've exhausted retries
                    logger.warning(f"Circuit breaker activated or endpoint failed: {str(e)}")
                    # Continue to the next URL
                    continue
            else:
                # For fallback endpoints, don't use circuit breaker but still limit retries
                while retry_count <= max_retries:
                    try:
                        # Use short timeouts for fallback endpoints
                        timeout = min(initial_timeout, 5)  # Max 5 seconds for fallback attempts

                        logger.info(f"Attempting fallback refresh token request (attempt {retry_count + 1}/{max_retries + 1}) at {token_url}", 
                                   extra={"endpoint": token_url, "timeout": timeout})

                        response = requests.post(token_url, data=data, headers=headers, timeout=timeout)

                        if response.status_code == 200:
                            logger.info(f"Fallback refresh token request successful at {token_url}")
                            return {
                                'status': 200,
                                'data': response.json(),
                                'endpoint': token_url
                            }
                        else:
                            # Handle non-200 status codes
                            try:
                                content = response.json()
                            except Exception:
                                content = response.text

                            logger.warning(f"Fallback refresh token request failed with status {response.status_code} at {token_url}", 
                                          extra={"endpoint": token_url, "response": content})

                            # If we get a 401 Unauthorized, don't retry this endpoint
                            if response.status_code == 401:
                                break

                            return {
                                'status': response.status_code,
                                'data': content,
                                'endpoint': token_url
                            }

                    except Timeout as e:
                        last_error = e
                        logger.warning(f"Fallback refresh token request timed out (attempt {retry_count + 1}/{max_retries + 1}) at {token_url}", 
                                      extra={"endpoint": token_url, "error": str(e)})

                        # If this is our last attempt for this URL, move to the next URL
                        if retry_count == max_retries:
                            logger.info(f"Moving to next endpoint after {max_retries + 1} timeouts at {token_url}")
                            break

                        retry_count += 1
                        continue

                    except ConnectionError as e:
                        last_error = e
                        logger.warning(f"Fallback refresh token request connection error (attempt {retry_count + 1}/{max_retries + 1}) at {token_url}", 
                                      extra={"endpoint": token_url, "error": str(e)})

                        # If this is our last attempt for this URL, move to the next URL
                        if retry_count == max_retries:
                            logger.info(f"Moving to next endpoint after {max_retries + 1} connection errors at {token_url}")
                            break

                        retry_count += 1
                        continue

                    except RequestException as e:
                        last_error = e
                        logger.warning(f"Fallback refresh token request failed (attempt {retry_count + 1}/{max_retries + 1}) at {token_url}", 
                                      extra={"endpoint": token_url, "error": str(e)})

                        # If this is our last attempt for this URL, move to the next URL
                        if retry_count == max_retries:
                            logger.info(f"Moving to next endpoint after {max_retries + 1} request errors at {token_url}")
                            break

                        retry_count += 1
                        continue

                # If we've exhausted all retries for this URL, move to the next URL
                logger.warning(f"Exhausted all retries for {token_url}, moving to next endpoint")

        # If we've tried all URLs and all failed
        logger.error("Refresh token request failed for all endpoints", 
                    extra={"primary_endpoint": primary_token_url, "fallback_urls": fallback_urls})
        return {
            'status': 504,
            'data': f'refresh token request failed for all endpoints',
            'endpoint': primary_token_url
        }
    except Exception as e:
        # Handle any unexpected errors
        logger.error(f"Unexpected error in refresh token request: {str(e)}")
        return {
            'status': 500,
            'data': f'unexpected error: {str(e)}',
            'endpoint': primary_token_url
        }




def tok_user_check(user):
    if UserProfile.objects.filter(id=user,is_active=True).exists():
        usertable=UserProfile.objects.get(id=user)
        data = {
            "status":200,
            "user_id":user,
            "usertable":usertable,
            "username":usertable.username,
            "email":usertable.email
        }
    else:
        data = {
            "status":404,
            "message":"User Not Activated, Please activate the account"
        }
    return data

def token_function(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    token = None
    if auth_header.startswith('Bearer '):
        token = auth_header.split('Bearer ')[1]
    try:
        token1=AccessToken.objects.get(token=token)
    except Exception as e:
        data = {"message":"Invalid Access Token",
                "status":404}
        return data
    user = token1.user_id
    if token1.expires < datetime.datetime.now(utc):
        ap_tb=Application.objects.get(id=token1.application_id) # token1
        if ap_tb.authorization_grant_type=="client_credentials":
            pass
        else:
            try:
                rf_token=RefreshToken.objects.get(access_token_id=token1.id,user_id=user)
            except:
                data = {"message":'Session Expired, Please login again',
                            "status":408}
                return data
            refresh_token=generate_access_from_refresh(rf_token.token)
            if refresh_token['status']==200:
                RefreshToken.objects.filter(id=rf_token.id).delete()
                AccessToken.objects.filter(id=token1.id).delete()
                pass
            else:
                RefreshToken.objects.filter(id=rf_token.id).delete()
                AccessToken.objects.filter(id=token1.id).delete()
                data = {"message":'Session Expired, Please login again',
                        "status":408}
                return data
    else:
        try:
            fn_data=tok_user_check(user)
            if fn_data["status"] == 200:
                # Add status to the returned data to ensure it's 200
                fn_data["status"] = 200
            return fn_data
        except:
            data = {
                "status":400,
                "message":"Admin not exists/Not assssigned/Role Not created"
            }
            return data      

