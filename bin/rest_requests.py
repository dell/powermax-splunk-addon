import json
import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class RestRequests:
    def __init__(self, username, password, verify, base_url, rest_timeout,
                 helper, array):
        self.username = username
        self.password = password
        self.verifySSL = verify
        self.base_url = base_url
        self.helper = helper
        self.array_id = array
        self.headers = {'content-type': 'application/json',
                        'accept': 'application/json'}
        self.session = self.establish_rest_session()

        if rest_timeout:
            self.rest_timeout = int(rest_timeout)
        else:
            self.rest_timeout = 60

    def establish_rest_session(self):
        session = requests.session()
        session.headers = self.headers
        session.auth = HTTPBasicAuth(self.username, self.password)
        session.verify = self.verifySSL
        return session

    def rest_request(self, target_url, method,
                     params=None, request_object=None):

        if not self.session:
            self.establish_rest_session()

        url = ("%(self.base_url)s%(target_url)s" %
               {'self.base_url': self.base_url,
                'target_url': target_url})
        try:
            if request_object:
                response = self.session.request(
                    method=method, url=url, timeout=self.rest_timeout,
                    data=json.dumps(request_object, sort_keys=True,
                                    indent=4))
            elif params:
                response = self.session.request(method=method,
                                                url=url,
                                                params=params,
                                                timeout=self.rest_timeout)
            else:
                response = self.session.request(method=method, url=url,
                                                timeout=self.rest_timeout)
            status_code = response.status_code

            try:
                response = response.json()

            except ValueError:
                self.helper.log_error(
                    "Array: %(array)s - No response received "
                    "from API. Status code received is: "
                    "%(status_code)s." % {
                        'array': self.array_id,
                        'status_code': status_code})
                response = None

            self.helper.log_debug(
                "Array: %(array)s - %(method)s request %(url)s returned with "
                "status code: %(status_code)s. Response: %(response)s." % {
                    'array': self.array_id,
                    'method': method,
                    'url': url,
                    'status_code': status_code,
                    'response': response})
            return response, status_code

        except requests.exceptions.SSLError:
            self.helper.log_error(
                ("Array: %(array)s - The %(method)s request to URL %(url)s "
                 "encountered an SSL issue. Please check your SSL cert "
                 "specified in the data input configuration and try "
                 "again.") % {
                    'array': self.array_id,
                    'method': method,
                    'url': url})

        except (requests.Timeout, requests.ConnectionError):
            self.helper.log_error(
                ("Array: %(array)s - The %(method)s request to URL %(url)s "
                 "timed-out, which may have been cause by a connection error. "
                 "Please check your data input coniguration and associated "
                 "instance of Unisphere.") % {
                    'array': self.array_id,
                    'method': method,
                    'url': url})

        except Exception as e:
            self.helper.log_error(
                ("Array: %(array)s - The %(method)s request to URL %(url)s "
                 "failed with exception %(e)s.") % {
                    'array': self.array_id,
                    'method': method,
                    'url': url,
                    'e': e})

    def close_session(self):
        """
        Close the current rest session
        """
        return self.session.close()
