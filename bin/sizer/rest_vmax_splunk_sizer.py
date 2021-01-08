import json
import requests
import sys
import time
import threading
import csv
import ConfigParser
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# HTTP constants
GET = 'GET'
POST = 'POST'
STATUS_200 = 200
STATUS_201 = 201
STATUS_202 = 202
STATUS_204 = 204
GLOBAL_TIMES = {}
CALL_COUNT = {}


class RestRequests:
    def __init__(self, username, password, verify, base_url, rest_timeout,
                 array, debug_enabled):
        self.username = username
        self.password = password
        self.verifySSL = verify
        self.base_url = base_url
        self.array_id = array
        self.headers = {'content-type': 'application/json',
                        'accept': 'application/json'}
        self.session = self.establish_rest_session()
        CALL_COUNT[self.array_id] = 0

        if str(debug_enabled.lower()) == 'true':
            self.debug_enabled = True
        else:
            self.debug_enabled = False

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

        CALL_COUNT[self.array_id] += 1

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
                print("Array: %(array)s - No response received "
                      "from API. Status code received is: "
                      "%(status_code)s." % {
                          'array': self.array_id,
                          'status_code': status_code})
                response = None

            if self.debug_enabled:
                print("Array: %(array)s - %(method)s request %(url)s returned "
                      "with status code: %(status_code)s. Response: "
                      "%(response)s." % {
                          'array': self.array_id,
                          'method': method,
                          'url': url,
                          'status_code': status_code,
                          'response': response})
            return response, status_code

        except requests.exceptions.SSLError:
            print("Array: %(array)s - The %(method)s request to URL %(url)s "
                  "encountered an SSL issue. Please check your SSL cert "
                  "specified in the data input configuration and try "
                  "again." % {
                      'array': self.array_id,
                      'method': method,
                      'url': url})

        except (requests.Timeout, requests.ConnectionError):
            print("Array: %(array)s - The %(method)s request to URL %(url)s "
                  "timed-out, which may have been cause by a connection "
                  "error. Please check your data input coniguration and "
                  "associated instance of Unisphere." % {
                      'array': self.array_id,
                      'method': method,
                      'url': url})

        except Exception as e:
            print(("Array: %(array)s - The %(method)s request to URL %(url)s "
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


class RestFunctions:
    def __init__(self, username=None, password=None, server_ip=None,
                 port=None, verify=None, u4v_version='84', array=None,
                 rest_timeout=None, debug_enabled=None):

        base_url = ('https://%(server_ip)s:%(port)s/univmax/restapi' % {
            'server_ip': str(server_ip),
            'port': str(port)})

        self.rest_client = RestRequests(username, password, verify,
                                        base_url, rest_timeout, array,
                                        debug_enabled)

        self.request = self.rest_client.rest_request
        self.server_ip = server_ip
        self.array_id = array
        self.u4v_version = u4v_version
        self.timestamp = None

    def make_request(self, target_uri, resource_type, method,
                     request_object=None,
                     params=None):
        def _check_status_code_success(operation, status_code, message):
            status_message = None

            if status_code not in [STATUS_200, STATUS_201,
                                   STATUS_202, STATUS_204]:

                response_codes = {
                    203: "Non-Authoritative Information",
                    205: "Reset Content",
                    206: "Partial Content",
                    301: "Moved Permanently",
                    304: "Not Modified",
                    305: "Use Proxy",
                    400: "Bad Request",
                    401: "Unauthorized - Please check Username & Password",
                    403: "Forbidden",
                    404: "Not Found",
                    405: "Method Not Allowed",
                    406: "Not Acceptable",
                    407: "Proxy Authentication Required",
                    408: "Request Timeout",
                    409: "Conflict",
                    410: "Gone",
                    412: "Precondition Failed",
                    413: "Request Entity Too Large",
                    414: "414 Request-URI Too Long",
                    415: "415 Unsupported Media Type",
                    417: "Expectation Failed",
                    500: "Internal Server Error",
                    501: "Not Implemented",
                    502: "Bad Gateway",
                    503: "Service Unavailable",
                    504: "Gateway Timeout",
                    505: "HTTP Version Not Supported"
                }

                try:
                    if message['message']:
                        status_message = (
                                "Error %(operation)s - Status code %(sc)s - "
                                "Message: %(message)s."
                                % {'operation': operation,
                                   'sc': status_code,
                                   'message': str(message['message'])})
                    else:
                        status_message = (
                                "Error %(operation)s - Status code %(sc)s - "
                                "Message: %(message)s."
                                % {'operation': operation,
                                   'sc': status_code,
                                   'message': message})
                except TypeError:
                    try:
                        status_message = (
                                "Error %(operation)s - Status code %(sc)s - "
                                "Message: %(message)s."
                                % {'operation': operation,
                                   'sc': status_code,
                                   'message': response_codes[
                                       int(status_code)]})
                    except KeyError:
                        status_message = (
                                "Error %(operation)s - Status code %(sc)s - "
                                "Message: %(message)s."
                                % {'operation': operation,
                                   'sc': status_code,
                                   'message': "Unknown Response Code, please "
                                              "check online for HTTP response "
                                              "code breakdown."})

            return status_message

        resource_object = None
        sc = None
        response = None

        try:
            response, sc = self.request(target_uri, method,
                                        request_object=request_object,
                                        params=params)
        except TypeError:
            print("Array: %(array)s - REST request failed." % {
                'array': self.array_id})
            exit("Exiting Metrics Run - Please check array connection.")

        rest_operation = '%(method)s %(res)s' % {
            'method': method,
            'res': resource_type}

        return_message = _check_status_code_success(rest_operation, sc,
                                                    response)
        if return_message:
            print("Array: %(array)s - REST request failed with: %(e)s" % {
                'array': self.array_id, 'e': return_message})

        if sc == STATUS_200:
            resource_object = response
        return resource_object

    def get_u4v_resource(self, method, category, resource_type,
                         resource_type_id=None, resource=None,
                         resource_id=None, request_object=None,
                         port_id=None, params=None):

        target_uri = self.build_uri(category, resource_type,
                                    resource_type_id, resource,
                                    resource_id, port_id)

        return self.make_request(target_uri=target_uri,
                                 resource_type=resource_type,
                                 method=method, request_object=request_object,
                                 params=params)

    def close_session(self):

        self.rest_client.close_session()

    def build_uri(self, category, resource_type,
                  resource_type_id=None, resource=None,
                  resource_id=None, port_id=None):

        target_uri = ("/%(category)s/%(resource_type)s" % {
            'category': category,
            'resource_type': resource_type})

        if resource_type_id:
            target_uri += "/%(resource_type_id)s" % {
                'resource_type_id': resource_type_id}

        if resource:
            target_uri += "/%(resource)s" % {
                'resource': resource}

        if resource_id:
            target_uri += "/%(resource_id)s" % {
                'resource_id': resource_id}

        if port_id:
            target_uri += "/port/%(port_id)s" % {
                'port_id': port_id}

        if "performance" not in category:
            target_uri = ("/%(version)s%(target)s" % {
                'version': self.u4v_version,
                'target': target_uri})

        return target_uri

    def merge_dicts(self, *dict_args):

        result = {}
        for dictionary in dict_args:
            if dictionary is not None:
                result.update(dictionary)
                for k, v in result.items():
                    if k in ['arrayId', 'symmetrixId', 'symmId',
                             'timestamp', 'array']:
                        result.pop(k)
            else:
                pass

        result['timestamp'] = self.timestamp
        result['array_id'] = self.array_id

        return json.dumps(result)

    def is_recent_timestamp(self):

        time_response = self.get_u4v_resource(method=GET,
                                              category='performance',
                                              resource_type='Array',
                                              resource='keys')

        current_timestamp = (int(time.time()) * 1000)
        array_timestamp = None

        for item in time_response['arrayInfo']:
            if item['symmetrixId'] == self.array_id:
                response = item
                array_timestamp = response['lastAvailableDate']

        if (current_timestamp - array_timestamp) < 540000:
            return True, array_timestamp
        else:
            return False, array_timestamp

    def validate_array(self):
        print("\tArray: %(array)s - Starting environment checks" % {
            'array': self.array_id})
        u4v_version = self.get_u4v_resource(method='GET',
                                            category='system',
                                            resource_type='version')

        # Check if Unisphere is responding
        if not u4v_version:
            print("Array: %(array)s - Unisphere not responding or is not "
                  "required 8.4 version. Please check corresponding status "
                  "code message above for further information. Is your VMAX "
                  "data input configured correctly? (IP Address, port, "
                  "username, password, SSL settings). Exiting metrics "
                  "collection run." % {'array': self.array_id})
            sys.exit("Array: %(array)s - Quit Collection Run" % {
                'array': self.array_id})

        print("\tArray: %(array)s - Check 1 Passed: U4V contact made." % {
            'array': self.array_id})

        # Check if Unisphere meets required version
        version_pass = False
        split_version = str(u4v_version['version']).split(".")
        major_version = list(split_version[0])
        if int(major_version[1]) == 9:
            version_pass = True
        elif int(major_version[1]) == 8:
            if int(split_version[1]) == 4 and int(split_version[3]) >= 10:
                version_pass = True

        if not version_pass:
            print("Array: %(array)s - Unishphere is not v8.4.0.10 or newer "
                  "version, please upgrade Unipshere to required version. "
                  "Exiting metrics collection run." % {'array': self.array_id})
            sys.exit("Array: %(array)s - Quit Collections Run" % {
                'array': self.array_id})

        print("\tArray: %(array)s - Check 2 Passed: U4V required 8.4.0.10 or "
              "newer." % {'array': self.array_id})

        # Check if VMAX is VMAX-3 model or newer
        isv3_response = self.get_u4v_resource(method='GET',
                                              category='sloprovisioning',
                                              resource_type='symmetrix',
                                              resource_type_id=self.array_id)

        if not isv3_response:
            print("Array: %(array)s - VMAX-3 or newer array not found, please "
                  "check array ID in data input configuration. Exiting metrics "
                  "collection run." % {'array': self.array_id})
            sys.exit("Array: %(array)s - Quit Collections Run." % {
                'array': self.array_id})
        print("\tArray: %(array)s - Check 3 Passed: VMAX-3 or newer "
              "array found." % {'array': self.array_id})

        # Check is VMAX local & performance registered
        perf_registered = False
        if isv3_response:
            is_perf = self.get_u4v_resource(method='GET',
                                            category='performance',
                                            resource_type='Array',
                                            resource='registration',
                                            resource_id=self.array_id)

            if is_perf['isRegistered']:
                perf_registered = True

        if not perf_registered:
            print("Array: %(array)s - VMAX array not performance registered "
                  "or is not local to Unisphere. Exiting metrics collection "
                  "run." % {'array': self.array_id})
            sys.exit("Array: %(array)s - Quit Collections Run" % {
                'array': self.array_id})

        print("\tArray: %(array)s - Check 4 Passed: VMAX array is "
              "performance registered." % {'array': self.array_id})

        # If performance registered, is timestamp up to date
        if isv3_response and perf_registered:
            time_true, timestamp = self.is_recent_timestamp()
            if time_true:
                self.timestamp = timestamp
                print("\tArray: %(array)s - Check 5 Passed: VMAX Array "
                      "timestamp is up to date: %(timestamp)s." % {
                          'array': self.array_id,
                          'timestamp': self.timestamp})
            else:
                print("Array: %(array)s - VMAX array performance timestamp "
                      "%(timestamp)s not current. Exiting metrics collection "
                      "run." % {
                          'array': self.array_id,
                          'timestamp': timestamp})
                sys.exit("Array: %(array)s - Quit Collections Run" % {
                    'array': self.array_id})

    def get_array_summary(self, array_id):
        array_summary_return = self.get_u4v_resource(
            method=GET, category='sloprovisioning', resource_type='symmetrix',
            resource_type_id=array_id)

        if array_summary_return:
            for k, v in array_summary_return['sloCompliance'].items():
                array_summary_return[('sloCompliance_%(k)s' % {'k': k})] = v
            for k, v in array_summary_return['physicalCapacity'].items():
                array_summary_return[('physicalCapacity_%(k)s' % {'k': k})] = v
            array_summary_return.pop('sloCompliance')
            array_summary_return.pop('physicalCapacity')
        else:
            array_summary_return['array_summary_details'] = False
            array_summary_return['array_summary_message'] = \
                "No Array summary info data available"

        array_system_return = self.get_u4v_resource(method=GET,
                                                    category='system',
                                                    resource_type='symmetrix',
                                                    resource_type_id=array_id)

        if not array_system_return:
            array_system_return['array_system_details'] = False
            array_system_return['array_system_message'] = \
                "No Array system summary data available"

        array_wlp_response = self.get_u4v_resource(
            method=GET, category='wlp', resource_type='capabilities',
            resource='symmetrix', resource_id=array_id)

        array_wlp_return = {}
        if array_wlp_response:
            array_wlp_return = array_wlp_response['symmetrixCapability'][0]
        else:
            array_wlp_return['array_wlp_details'] = False
            array_wlp_return['array_wlp_message'] = \
                "No Array WLP summary data available"

        array_migration_response = self.get_u4v_resource(
            method=GET, category='migration', resource_type='capabilities',
            resource='symmetrix')

        array_migration_return = {}
        if array_migration_response:
            for item in array_migration_response['storageArrayCapability']:
                if item['arrayId'] == self.array_id:
                    array_migration_return = item
        else:
            array_migration_return['array_migration_details'] = False
            array_migration_return['array_migration_message'] = \
                "No Array migration summary data available"

        array_rep_cap_response = self.get_u4v_resource(
            method=GET, category='replication', resource_type='capabilities',
            resource='symmetrix')

        array_rep_cap_return = {}
        if array_rep_cap_response:
            for item in array_rep_cap_response['symmetrixCapability']:
                if item['symmetrixId'] == self.array_id:
                    array_rep_cap_return = item
        else:
            array_rep_cap_return['array_rep_cap_details'] = False
            array_rep_cap_return['array_rep_cap_message'] = \
                "No Array replication capabilities data available"

        array_replication_return = self.get_u4v_resource(
            method=GET, category='replication', resource_type='symmetrix',
            resource_type_id=array_id)

        if not array_replication_return:
            array_replication_return = dict()
            array_replication_return['array_replication_details'] = False
            array_replication_return['array_replication_message'] = \
                "No Array replication summary data available"

        array_alert_details = self.get_u4v_resource(
            method=GET, category='system', resource_type='alert_summary')

        aar = {}
        found_symm = False
        if array_alert_details:
            for item in array_alert_details['symmAlertSummary']:
                if item['symmId'] == self.array_id:
                    found_symm = True
                    aar = item
                    for k, v in aar['performanceAlertSummary'].items():
                        aar[('performanceAlertSummary_%(k)s' % {'k': k})] = v
                    aar.pop('performanceAlertSummary')
                    for k, v in aar['arrayAlertSummary'].items():
                        aar[('arrayAlertSummary_%(k)s' % {'k': k})] = v
                    aar.pop('arrayAlertSummary')
        if not found_symm:
            aar['array_alert_details'] = False
            aar['array_alert_message'] = \
                "No Array alerts summary data available"

        array_perf_payload = {
            'startDate': str(self.timestamp),
            'symmetrixId': self.array_id,
            'metrics': [
                'CriticalAlertCount', 'InfoAlertCount', 'WarningAlertCount',
                'AllocatedCapacity', 'AvgFallThruTime', 'Cache_Balance',
                'DA_Balance', 'DX_Balance', 'EFD_Balance', 'FC_Balance',
                'FE_Balance', 'RDF_Balance', 'SATA_Balance', 'BEIOs',
                'BEReadReqs', 'BEUtilization', 'BEWriteReqs', 'BEReqs',
                'OverallCompressionRatio', 'CopySlotCount', 'DeviceWPEvents',
                'OverallEfficiencyRatio', 'FEReadReqs', 'FEUtilization',
                'FEWriteReqs', 'HostMBs', 'FEHitReqs', 'HardwareHealthScore',
                'HostIOs', 'HostMBReads', 'HostMBWritten', 'DiskUtilization',
                'AvgOptimizedReadMissSize', 'OptimizedMBReadMisses',
                'OptimizedReadMisses', 'OverallHealthScore', 'FEWriteMissReqs',
                'PercentEffectiveUsedCapacity', 'PercentHit', 'WPCount',
                'PercentMetaRepUsed', 'PercentMetaSystemUsed', 'FEReqs',
                'PercentReads', 'PercentSnapshotSaved', 'VPCompressionRatio',
                'PercentSubscribedCapacity', 'PercentVPSaved', 'PercentWrites',
                'PrefetchedTracks', 'QueueDepthUtilization', 'RDFA_WPCount',
                'RDFUtilization', 'FEReadHitReqs', 'FEReadMissReqs',
                'SloHealthScore', 'SnapshotCompressionRatio', 'HostReads',
                'SnapshotEfficiencyRatio', 'SnapshotSharedRatio',
                'SubscribedCapacity', 'SoftwareHealthScore', 'SystemWPEvents',
                'PercentCacheWP', 'UsableCapacity', 'WriteResponseTime',
                'VPEfficiencyRatio', 'VPSharedRatio', 'ReadResponseTime',
                'SystemMaxWPLimit', 'HostWrites', 'FEWriteHitReqs',
            ],
            'dataFormat': "Average",
            'endDate': str(self.timestamp)
        }

        array_perf_response = self.get_u4v_resource(
            method=POST, category='performance', resource_type='Array',
            resource='metrics', request_object=array_perf_payload)

        array_perf_return = {}
        if array_perf_response:
            array_perf_return = array_perf_response['resultList']['result'][0]
        else:
            array_perf_return['array_perf_details'] = False
            array_perf_return['array_perf_message'] = \
                "No Array performance data available"

        array_perf_return['reporting_level'] = "Array"

        return self.merge_dicts(array_summary_return, array_system_return,
                                array_wlp_return, array_migration_return,
                                array_rep_cap_return, aar,
                                array_replication_return, array_perf_return)

    def get_alert_list(self, symm_only=None):
        if symm_only:
            params = {'description': '<like>%(array_id)s' % {
                'array_id': self.array_id}}
        else:
            params = None

        array_alert_details = self.get_u4v_resource(method=GET,
                                                    category='system',
                                                    resource_type='alert',
                                                    params=params)
        return array_alert_details['alertId']

    def get_symm_alert_details(self, alert_id):
        array_alert_details = self.get_u4v_resource(method=GET,
                                                    category='system',
                                                    resource_type='alert',
                                                    resource_type_id=alert_id)

        array_id = self.array_id
        if "Object is" in array_alert_details['description']:
            split_string = array_alert_details['description'].split(':')
            del split_string[0]
            alert_array_id = split_string[0].strip()
            asset_id = split_string[1].strip()

        elif str(array_id) in array_alert_details['description']:
            message_pt1 = array_alert_details['description']
            message_pt2 = "Asset ID unknown, please check Unisphere for " \
                          "more specific details"
            full_msg = ("%(message_pt1)s. %(message_pt2)s" % {
                'message_pt1': message_pt1,
                'message_pt2': message_pt2})

            array_alert_details['description'] = full_msg
            alert_array_id = self.array_id
            asset_id = "Unknown"

        elif 'Array metadata usage' in array_alert_details['description']:
            message_pt1 = array_alert_details['description']
            message_pt2 = "Array ID unknown, check Array Summary dashboard " \
                          "for % System Metadata Usage"
            full_msg = ('%(message_pt1)s. %(message_pt2)s' % {
                'message_pt1': message_pt1,
                'message_pt2': message_pt2})

            array_alert_details['description'] = full_msg
            alert_array_id = "Unknown"
            asset_id = "Unknown"

        else:
            message_pt1 = array_alert_details['description']
            message_pt2 = "VMAX & Asset ID unknown, please check Unisphere " \
                          "for more specific details"
            full_msg = ("%(message_pt1)s. %(message_pt2)s" % {
                'message_pt1': message_pt1,
                'message_pt2': message_pt2})

            array_alert_details['description'] = full_msg
            alert_array_id = "Unknown"
            asset_id = "Unknown"

        array_alert_details['reporting_level'] = "Alert"
        array_alert_details['array_id'] = alert_array_id
        array_alert_details['asset_id'] = asset_id
        array_alert_details['timestamp'] = self.timestamp
        array_alert_details['u4v_source'] = self.server_ip

        return json.dumps(array_alert_details)

    def get_srp_list(self):
        array_srp_details = self.get_u4v_resource(
            method=GET, category='sloprovisioning', resource_type='symmetrix',
            resource_type_id=self.array_id, resource='srp')

        return array_srp_details['srpId']

    def get_srp_details(self, srp_id):
        srp_details = self.get_u4v_resource(method=GET,
                                            category='sloprovisioning',
                                            resource_type='symmetrix',
                                            resource_type_id=self.array_id,
                                            resource='srp', resource_id=srp_id)
        try:
            srp_details.pop('srpSgDemandId')
        except KeyError:
            pass
        try:
            srp_details.pop('diskGroupId')
        except KeyError:
            pass

        srp_perf_payload = {
            'symmetrixId': self.array_id,
            'endDate': self.timestamp,
            'srpId': srp_id,
            'dataFormat': "Average",
            'metrics': [
                'BEMBReads', 'BEMBTransferred', 'BEMBWritten', 'BEReadReqs',
                'BEWriteReqs', 'OverallCompressionRatio', 'HostMBWritten',
                'OverallEfficiencyRatio', 'HostMBs', 'HostIOs', 'HostMBReads',
                'PercentSnapshotSaved', 'SnapshotEfficiencyRatio', 'BEReqs',
                'PercentVPSaved', 'HostReads', 'ResponseTime', 'HostWrites',
                'VPSharedRatio', 'ReadResponseTime', 'WriteResponseTime',
                'SnapshotSharedRatio', 'TotalSRPCapacity', 'UsedSRPCapacity',
                'VPCompressionRatio', 'VPEfficiencyRatio',
                'SnapshotCompressionRatio',
            ],
            'startDate': self.timestamp
        }

        srp_perf_response = self.get_u4v_resource(
            method=POST, category='performance', resource_type='SRP',
            resource='metrics', request_object=srp_perf_payload)

        srp_details['reporting_level'] = "SRP"

        return self.merge_dicts(srp_details,
                                srp_perf_response['resultList']['result'][0])

    def get_sg_list(self):
        array_sg_details = self.get_u4v_resource(
            method=GET, category='sloprovisioning', resource_type='symmetrix',
            resource_type_id=self.array_id, resource='storagegroup')

        return array_sg_details['storageGroupId']

    def get_sg_details(self, sg_id):
        sg_details = self.get_u4v_resource(method=GET,
                                           category='sloprovisioning',
                                           resource_type='symmetrix',
                                           resource_type_id=self.array_id,
                                           resource='storagegroup',
                                           resource_id=sg_id)

        default_value = "NONE"
        try:
            sg_details.get('slo')
        except AttributeError:
            sg_details['slo'] = default_value

        try:
            sg_details.get('workload')
        except AttributeError:
            sg_details['workload'] = default_value

        try:
            sg_details.get('srp')
        except AttributeError:
            sg_details['srp'] = default_value

        sg_perf_payload = {
            'symmetrixId': self.array_id,
            'endDate': self.timestamp,
            'dataFormat': "Average",
            'storageGroupId': sg_id,
            'metrics': [
                'CriticalAlertCount', 'InfoAlertCount', 'WarningAlertCount',
                'AllocatedCapacity', 'TotalTracks', 'BEDiskReadResponseTime',
                'BEReadRequestTime', 'BEReadTaskTime', 'AvgIOSize',
                'AvgReadResponseTime6', 'AvgReadResponseTime7', 'AvgReadSize',
                'AvgWritePacedDelay', 'AvgWriteResponseTime6', 'AvgWriteSize',
                'AvgWriteResponseTime7', 'BEMBReads', 'BEMBTransferred',
                'BEPercentReads', 'BEMBWritten', 'BEPercentWrites',
                'BEPrefetchedTrackss', 'BEPrefetchedTrackUsed', 'BEReadReqs',
                'BEWriteReqs', 'CompressedTracks', 'CompressionRatio',
                'BlockSize', 'HostMBs', 'IODensity', 'HostIOs', 'RdfReadHits',
                'MaxWPThreshold', 'HostMBReads', 'HostMBWritten', 'RdfReads',
                'PercentCompressedTracks', 'PercentHit', 'PercentMisses',
                'PercentRandomIO', 'PercentRandomReads', 'PercentRead',
                'PercentRandomReadHit', 'PercentRandomReadMiss', 'RdfMBRead',
                'PercentRandomWrites', 'PercentRandomWriteHit', 'RdfMBWritten',
                'PercentRandomWriteMiss', 'PercentReadHit', 'PercentReadMiss',
                'PercentSeqRead', 'PercentSeqIO', 'PercentSeqReadHit',
                'PercentSeqReadMiss', 'PercentSeqWrites', 'PercentSeqWriteHit',
                'PercentSeqWriteMiss', 'PercentVPSpaceSaved', 'PercentWrite',
                'PercentWriteHit', 'PercentWriteMiss', 'BEPrefetchedMBs',
                'HostIOLimitPercentTimeExceeded', 'RandomIOs', 'HostReadHits',
                'RandomReadHits', 'RandomReadMisses', 'RandomReads',
                'RandomWriteHits', 'RandomWriteMisses', 'RandomWrites',
                'RdfResponseTime', 'RDFRewrites', 'RdfWrites', 'HostReads',
                'HostReadMisses', 'ReadResponseTimeCount1', 'ResponseTime',
                'ReadResponseTimeCount2', 'ReadResponseTimeCount3',
                'ReadResponseTimeCount4', 'ReadResponseTimeCount5',
                'ReadResponseTimeCount6', 'ReadResponseTimeCount7',
                'RDFS_WriteResponseTime', 'ReadMissResponseTime',
                'ReadResponseTime', 'WriteMissResponseTime', 'SeqReadHits',
                'WriteResponseTime', 'SeqReadMisses', 'SeqReads', 'Skew',
                'SeqWriteHits', 'SeqWriteMisses', 'SeqWrites', 'SRDFA_MBSent',
                'SRDFA_WriteReqs', 'SRDFS_MBSent', 'SRDFS_WriteReqs', 'BEReqs',
                'HostHits', 'HostMisses', 'SeqIOs', 'WPCount', 'HostWrites',
                'HostWriteHits', 'HostWriteMisses', 'WritePacedDelay',
                'WriteResponseTimeCount1', 'WriteResponseTimeCount2',
                'WriteResponseTimeCount3', 'WriteResponseTimeCount4',
                'WriteResponseTimeCount5', 'WriteResponseTimeCount6',
                'WriteResponseTimeCount7'
            ],
            'startDate': self.timestamp
        }

        srp_perf_response = self.get_u4v_resource(
            method=POST, category='performance', resource_type='StorageGroup',
            resource='metrics', request_object=sg_perf_payload)

        sg_details['reporting_level'] = "SG"

        return self.merge_dicts(sg_details,
                                srp_perf_response['resultList']['result'][0])

    def get_director_list(self):
        array_director_list = self.get_u4v_resource(
            method=GET, category='sloprovisioning', resource_type='symmetrix',
            resource_type_id=self.array_id, resource='director')

        return array_director_list['directorId']

    def get_director_details(self, director_id):
        array_director_details = self.get_u4v_resource(
            method=GET, category='sloprovisioning', resource_type='symmetrix',
            resource_type_id=self.array_id, resource='director',
            resource_id=director_id)

        dir_perf_response = {}
        if 'DF' in director_id or 'DX' in director_id:
            dir_perf_payload = {
                'symmetrixId': self.array_id,
                'directorId': director_id,
                'endDate': self.timestamp,
                'dataFormat': "Average",
                'metrics': [
                    'AvgTimePerSyscall', 'CompressedMBs', 'CompressedReadMBs',
                    'CompressedWriteMBs', 'CompressedReadReqs', 'MBWritten',
                    'CompressedReqs', 'CompressedWriteReqs', 'IOs', 'MBs',
                    'MBRead', 'PercentBusy', 'PercentBusyLogicalCore_0',
                    'PercentBusyLogicalCore_1', 'PercentNonIOBusy',
                    'PercentNonIOBusyLogicalCore_0', 'Syscall_RDF_DirCount',
                    'PercentNonIOBusyLogicalCore_1', 'PercentReadReqs',
                    'PercentWriteReqs', 'PrefetchedTracks', 'ReadReqs', 'Reqs',
                    'SyscallCount', 'SyscallRemoteDirCount', 'WriteReqs'
                ],
                'startDate': self.timestamp
            }

            response = self.get_u4v_resource(method=POST,
                                             category='performance',
                                             resource_type='BEDirector',
                                             resource='metrics',
                                             request_object=dir_perf_payload)
            if response:
                dir_perf_response = response['resultList']['result'][0]
            else:
                dir_perf_response['director_perf_details'] = False
                dir_perf_response['director_perf_message'] = \
                    "No active Director performance data available"
            dir_perf_response['director_type'] = "BE"

        elif "EF" in director_id or "FA" in director_id \
                or "FE" in director_id or "SE" in director_id:
            dir_perf_payload = {
                'symmetrixId': self.array_id,
                'directorId': director_id,
                'endDate': self.timestamp,
                'dataFormat': "Average",
                'metrics': [
                    'AvgQueueDepthRange0', 'AvgQueueDepthRange1',
                    'AvgQueueDepthRange2', 'AvgQueueDepthRange3',
                    'AvgQueueDepthRange4', 'AvgQueueDepthRange5',
                    'AvgQueueDepthRange6', 'AvgQueueDepthRange7',
                    'AvgQueueDepthRange8', 'AvgQueueDepthRange9',
                    'AvgRDFSWriteResponseTime', 'AvgReadMissResponseTime',
                    'AvgWPDiscTime', 'AvgTimePerSyscall', 'DeviceWPEvents',
                    'HostMBs', 'HitReqs', 'HostIOs', 'MissReqs',
                    'AvgOptimizedReadMissSize', 'OptimizedMBReadMisses',
                    'OptimizedReadMisses', 'PercentBusy', 'PercentWriteReqs',
                    'PercentBusyLogicalCore_0', 'PercentBusyLogicalCore_1',
                    'PercentHitReqs', 'PercentReadReqs', 'PercentReadReqHit',
                    'PercentWriteReqHit', 'QueueDepthUtilization',
                    'QueueDepthCountRange0', 'QueueDepthCountRange1',
                    'QueueDepthCountRange2', 'QueueDepthCountRange3',
                    'QueueDepthCountRange4', 'QueueDepthCountRange5',
                    'QueueDepthCountRange6', 'QueueDepthCountRange7',
                    'QueueDepthCountRange8', 'QueueDepthCountRange9',
                    'HostIOLimitIOs', 'HostIOLimitMBs', 'ReadReqs',
                    'ReadHitReqs', 'ReadMissReqs',
                    'ReadRTCountRange0To1', 'ReadRTCountRange16To32',
                    'ReadRTCountRange1To2', 'ReadRTCountRange2To4',
                    'ReadRTCountRange32To64', 'ReadRTCountRange4To8',
                    'ReadRTCountRange8To16', 'ReadRTCountRangeover64', 'Reqs',
                    'ReadResponseTime', 'WriteResponseTime', 'SlotCollisions',
                    'SyscallCount', 'Syscall_RDF_DirCounts',
                    'SyscallRemoteDirCounts', 'SystemWPEvents',
                    'TotalReadCount', 'TotalWriteCount', 'WriteReqs',
                    'WriteHitReqs', 'WriteMissReqs',
                    'WriteRTCountRange0To1', 'WriteRTCountRange16To32',
                    'WriteRTCountRange1To2', 'WriteRTCountRange2To4',
                    'WriteRTCountRange32To64', 'WriteRTCountRange4To8',
                    'WriteRTCountRange8To16', 'WriteRTCountRangeover64'
                ],
                'startDate': self.timestamp
            }
            response = self.get_u4v_resource(method=POST,
                                             category='performance',
                                             resource_type='FEDirector',
                                             resource='metrics',
                                             request_object=dir_perf_payload)

            if response:
                dir_perf_response = response['resultList']['result'][0]
            else:
                dir_perf_response['director_perf_details'] = False
                dir_perf_response['director_perf_message'] = \
                    "No active Director performance data available"
            dir_perf_response['director_type'] = "FE"

        elif "RF" in director_id or "RE" in director_id:
            try:
                array_director_details['num_srdf_groups'] = \
                    len(array_director_details['srdf_groups'])
                array_director_details.pop('srdf_groups')
            except KeyError:
                array_director_details['num_srdf_groups'] = 0

            dir_perf_payload = {
                'symmetrixId': self.array_id,
                'directorId': director_id,
                'endDate': self.timestamp,
                'dataFormat': "Average",
                'metrics': [
                    'AvgIOServiceTime', 'AvgIOSizeReceived', 'AvgIOSizeSent',
                    'AvgTimePerSyscall', 'CompresedMBSentAndReceived',
                    'CompresedMBReceived', 'CompresedMBSent', 'CopyIOs',
                    'CopyMBs', 'IOs', 'MBSentAndReceived', 'MBRead',
                    'MBWritten', 'NumberOfCompresedLinks', 'PercentBusy',
                    'NumberOfLinks', 'PercentCompresedMBSentAndReceived',
                    'PercentCompresedMBReceived', 'PercentCompresedMBSent',
                    'Reqs', 'Rewrites', 'AsyncMBSent', 'AsyncWriteReqs',
                    'SyncWrites', 'SyscallCount', 'SyncMBSent', 'SyscallTime',
                    'Syscall_RDF_DirCounts', 'SyscallRemoteDirCount',
                    'TracksReceivedPerSec', 'TracksSentPerSec', 'WriteReqs'
                ],
                'startDate': self.timestamp
            }
            response = self.get_u4v_resource(method=POST,
                                             category='performance',
                                             resource_type='RDFDirector',
                                             resource='metrics',
                                             request_object=dir_perf_payload)

            if response:
                dir_perf_response = response['resultList']['result'][0]
            else:
                dir_perf_response['director_perf_details'] = False
                dir_perf_response['director_perf_message'] = \
                    "No active Director performance data available"
            dir_perf_response['director_type'] = "RDF"

        elif "IM" in director_id:
            dir_perf_payload = {
                'symmetrixId': self.array_id,
                'directorId': director_id,
                'endDate': self.timestamp,
                'dataFormat': "Average",
                'metrics': ['PercentBusy'],
                'startDate': self.timestamp
            }
            response = self.get_u4v_resource(method=POST,
                                             category='performance',
                                             resource_type='IMDirector',
                                             resource='metrics',
                                             request_object=dir_perf_payload)
            if response:
                dir_perf_response = response['resultList']['result'][0]
            else:
                dir_perf_response['director_perf_details'] = False
                dir_perf_response['director_perf_message'] = \
                    "No active Director performance data available"
            dir_perf_response['director_type'] = "IM"

        elif "ED" in director_id:
            dir_perf_payload = {
                'symmetrixId': self.array_id,
                'directorId': director_id,
                'endDate': self.timestamp,
                'dataFormat': "Average",
                'metrics': [
                    'PercentBusy', 'RandomReadMissMBs', 'RandomReadMisses',
                    'RandomWriteMissMBs', 'RandomWriteMisses'
                ],
                'startDate': self.timestamp
            }
            response = self.get_u4v_resource(method=POST,
                                             category='performance',
                                             resource_type='EDSDirector',
                                             resource='metrics',
                                             request_object=dir_perf_payload)
            if response:
                dir_perf_response = response['resultList']['result'][0]
            else:
                dir_perf_response['director_perf_details'] = False
                dir_perf_response['director_perf_message'] = \
                    "No active Director performance data available"
            dir_perf_response['director_type'] = "EDS"

        else:
            dir_perf_response = {
                'perf_metrics_payload': False,
                'director_type': "N/A"
            }

        array_director_details['reporting_level'] = "Director"

        return self.merge_dicts(array_director_details, dir_perf_response)

    def get_pg_list(self):
        array_pg_list = self.get_u4v_resource(method=GET,
                                              category='sloprovisioning',
                                              resource_type='symmetrix',
                                              resource_type_id=self.array_id,
                                              resource='portgroup')
        return array_pg_list['portGroupId']

    def get_pg_details(self, pg_id):
        pg_details = self.get_u4v_resource(method=GET,
                                           category='sloprovisioning',
                                           resource_type='symmetrix',
                                           resource_type_id=self.array_id,
                                           resource='portgroup',
                                           resource_id=pg_id)

        pg_details['port_list'] = []
        try:
            for item in pg_details['symmetrixPortKey']:
                pg_details['port_list'].append(item['portId'])
            pg_details.pop('symmetrixPortKey')
        except KeyError:
            pass

        pg_payload = {
            'symmetrixId': self.array_id,
            'portGroupId': pg_id,
            'endDate': self.timestamp,
            'dataFormat': "Average",
            'metrics': [
                'AvgIOSize', 'IOs', 'MBs', 'MBRead', 'MBWritten',
                'PercentBusy', 'Reads', 'Writes'
            ],
            'startDate': self.timestamp
        }

        pg_perf_response = self.get_u4v_resource(method=POST,
                                                 category='performance',
                                                 resource_type='PortGroup',
                                                 resource='metrics',
                                                 request_object=pg_payload)

        pg_details['reporting_level'] = "Port Group"

        return self.merge_dicts(pg_details,
                                pg_perf_response['resultList']['result'][0])

    def get_port_list(self):
        array_port_list = self.get_u4v_resource(method=GET,
                                                category='sloprovisioning',
                                                resource_type='symmetrix',
                                                resource_type_id=self.array_id,
                                                resource='port')
        return array_port_list['symmetrixPortKey']

    def get_port_details(self, port_key):
        port_id = port_key['portId']
        director_id = port_key['directorId']

        port_details = self.get_u4v_resource(method=GET,
                                             category='sloprovisioning',
                                             resource_type='symmetrix',
                                             resource_type_id=self.array_id,
                                             resource='director',
                                             resource_id=director_id,
                                             port_id=port_id)

        port_details['symmetrixPort'].pop('symmetrixPortKey')

        port_response = {}
        port_perf_response = {}

        port_type = "Unknown"

        if "DF" in director_id or "DX" in director_id:
            port_type = "Back End Director"
            port_payload = {
                'startDate': self.timestamp,
                'symmetrixId': self.array_id,
                'metrics': [
                    'AvgIOSize', 'IOs', 'MaxSpeedGBs', 'MBs',
                    'MBRead', 'MBWritten', 'PercentBusy', 'Reads', 'Writes'
                ],
                'directorId': director_id,
                'dataFormat': "Average",
                'endDate': self.timestamp,
                'portId': port_id
            }

            port_perf_response = self.get_u4v_resource(
                method=POST, category='performance', resource_type='BEPort',
                resource='metrics', request_object=port_payload)

        elif "EF" in director_id or "FA" in director_id \
                or "FE" in director_id or "SE" in director_id:
            port_type = "Front End Director"
            port_payload = {
                'startDate': self.timestamp,
                'symmetrixId': self.array_id,
                'metrics': [
                    'AvgIOSize', 'IOs', 'MaxSpeedGBs', 'MBs', 'MBRead',
                    'MBWritten', 'PercentBusy', 'Reads', 'ResponseTime',
                    'ReadResponseTime', 'WriteResponseTime', 'SpeedGBs',
                    'Writes'
                ],
                'directorId': director_id,
                'dataFormat': "Average",
                'endDate': self.timestamp,
                'portId': port_id
            }

            port_perf_response = self.get_u4v_resource(
                method=POST, category='performance', resource_type='FEPort',
                resource='metrics', request_object=port_payload)

        elif "RF" in director_id or "RE" in director_id:
            port_type = "RDF Director"
            port_payload = {
                'startDate': self.timestamp,
                'symmetrixId': self.array_id,
                'metrics': [
                    'AvgIOSize', 'IOs', 'MaxSpeedGBs', 'MBs', 'MBRead',
                    'MBWritten', 'PercentBusy', 'Reads', 'SpeedGBs', 'Writes'
                ],
                'directorId': director_id,
                'dataFormat': "Average",
                'endDate': self.timestamp,
                'portId': port_id
            }

            port_perf_response = self.get_u4v_resource(
                method=POST, category='performance', resource_type='RDFPort',
                resource='metrics', request_object=port_payload)

        if port_perf_response:
            port_response = port_perf_response['resultList']['result'][0]
        else:
            port_response['port_perf_details'] = False
            port_response['port_perf_message'] = \
                "No active Port performance data available"

        port_response['reporting_level'] = "Port"
        port_response['port_id'] = port_id
        port_response['port_dir_type'] = port_type
        port_response['director_id'] = director_id
        port_response['dir_port_key'] = "%(director_id)s:%(port_id)s" % \
                                        {'director_id': director_id,
                                         'port_id': port_id}

        return self.merge_dicts(port_details['symmetrixPort'], port_response)

    def get_host_list(self):
        array_host_list = self.get_u4v_resource(method=GET,
                                                category='sloprovisioning',
                                                resource_type='symmetrix',
                                                resource_type_id=self.array_id,
                                                resource='host')

        host_key_payload = {
            'startDate': self.timestamp,
            'symmetrixId': self.array_id,
            'endDate': self.timestamp
        }

        active_host_response = self.get_u4v_resource(
            method=POST, category='performance', resource_type='Host',
            resource='keys', request_object=host_key_payload)

        active_host_list = []
        for item in active_host_response['hostInfo']:
            host_id = item['hostId']
            active_host_list.append(host_id)

        return array_host_list['hostId'], active_host_list

    def get_host_details(self, host_id, active_host_list):

        host_details = self.get_u4v_resource(method=GET,
                                             category='sloprovisioning',
                                             resource_type='symmetrix',
                                             resource_type_id=self.array_id,
                                             resource='host',
                                             resource_id=host_id)

        # Change enabled_flags from CSL to list
        try:
            old_flag_list = host_details['enabled_flags'].split(')')
            old_flag_list.remove('')
            host_details['enabled_flags'] = []
            for flag in old_flag_list:
                host_details['enabled_flags'].append(flag.replace(',', ''))
            if len(host_details['enabled_flags']) == 0:
                host_details['enabled_flags'] = ["N/A"]
        except KeyError:
            pass

        # Change disabled_flags from CSL to list
        try:
            old_flag_list = host_details['disabled_flags'].split(')')
            old_flag_list.remove('')
            host_details['disabled_flags'] = []
            for flag in old_flag_list:
                host_details['disabled_flags'].append(flag.replace(',', ''))
            if len(host_details['disabled_flags']) == 0:
                host_details['disabled_flags'] = ["N/A"]
        except KeyError:
            pass

        host_perf_response = {}
        if host_id in active_host_list:

            host_payload = {
                'symmetrixId': self.array_id,
                'endDate': self.timestamp,
                'dataFormat': "Average",
                'hostId': host_id,
                'metrics': [
                    'HostIOs', 'MBs', 'HostMBReads', 'HostMBWrites',
                    'Reads', 'ResponseTime', 'ReadResponseTime',
                    'WriteResponseTime', 'SyscallCount', 'Writes'
                ],
                'startDate': self.timestamp
            }

            host_perf_response = self.get_u4v_resource(
                method=POST, category='performance', resource_type='Host',
                resource='metrics', request_object=host_payload)

            host_perf_response = host_perf_response['resultList']['result'][0]
        else:
            host_details['host_perf_details'] = False
            host_details['host_perf_message'] = \
                "No active Host performance data available"

        host_details['reporting_level'] = "Host"

        return self.merge_dicts(host_details, host_perf_response)

    def get_initiator_list(self):
        initiator_list = self.get_u4v_resource(method=GET,
                                               category='sloprovisioning',
                                               resource_type='symmetrix',
                                               resource_type_id=self.array_id,
                                               resource='initiator')

        initiator_key_payload = {
            'startDate': self.timestamp,
            'symmetrixId': self.array_id,
            'endDate': self.timestamp
        }

        active_init_response = self.get_u4v_resource(
            method=POST, category='performance', resource_type='Initiator',
            resource='keys', request_object=initiator_key_payload)

        active_initiator_list = []
        for item in active_init_response['initiatorInfo']:
            init_id = item['initiatorId']
            active_initiator_list.append(init_id)

        return initiator_list['initiatorId'], active_initiator_list

    def get_initiator_details(self, initiator_id, active_initiator_list):

        initiator_details = self.get_u4v_resource(
            method=GET, category='sloprovisioning', resource_type='symmetrix',
            resource_type_id=self.array_id, resource='initiator',
            resource_id=initiator_id)

        dir_port_keys = []
        for item in initiator_details['symmetrixPortKey']:
            director_id = item['directorId']
            port_id = item['portId']
            dir_port_key = "%(director_id)s:%(port_id)s" % {
                'director_id': director_id, 'port_id': port_id}
            dir_port_keys.append(dir_port_key)

        initiator_details['dir_port_keys'] = dir_port_keys
        initiator_details.pop('symmetrixPortKey')

        # Change flags_in_effect from CSL to list
        try:
            old_flag_list = initiator_details['flags_in_effect'].split()
            initiator_details['flags_in_effect'] = []
            for flag in old_flag_list:
                initiator_details['flags_in_effect'].append(
                    flag.replace(',', ''))
        except KeyError:
            pass

        # Change enabled_flags from CSL to list
        try:
            old_flag_list = initiator_details['enabled_flags'].split()
            initiator_details['enabled_flags'] = []
            for flag in old_flag_list:
                initiator_details['enabled_flags'].append(
                    flag.replace(',', ''))
        except KeyError:
            pass

        # Change disabled_flags from CSL to list
        try:
            old_flag_list = initiator_details['disabled_flags'].split()
            initiator_details['disabled_flags'] = []
            for flag in old_flag_list:
                initiator_details['disabled_flags'].append(
                    flag.replace(',', ''))
        except KeyError:
            pass

        initiator_perf_response = {}

        # Initiator is FC - get performance stats
        if "iqn" not in initiator_id:
            temp_perf = initiator_id.split(':')
            perf_init_id = temp_perf[2]
            if perf_init_id in active_initiator_list:

                initiator_perf_payload = {
                    'symmetrixId': self.array_id,
                    'endDate': self.timestamp,
                    'dataFormat': "Average",
                    'initiatorId': perf_init_id,
                    'metrics': [
                        'HostIOs', 'MBs', 'HostMBReads', 'HostMBWrites',
                        'Reads', 'ResponseTime', 'ReadResponseTime',
                        'WriteResponseTime', 'SyscallCount', 'Writes'
                    ],
                    'startDate': self.timestamp
                }

                initiator_perf_response = self.get_u4v_resource(
                    method=POST, category='performance',
                    resource_type='Initiator',
                    resource='metrics', request_object=initiator_perf_payload)

                if initiator_perf_response:
                    initiator_perf_response = \
                        initiator_perf_response['resultList']['result'][0]
                    initiator_perf_response['performance_metrics'] = True
            else:
                initiator_details['initiator_perf_details'] = False
                initiator_details['initiator_perf_message'] = \
                    "No active Initiator performance data available"

        # Initiator is iSCSI - no performance stats available
        elif "iqn" in initiator_id:
            initiator_details['initiator_perf_details'] = False
            initiator_details['initiator_perf_message'] = \
                "No iSCSI Initiator performance data available"

        try:
            initiator_details['host_id'] = initiator_details['host']
            initiator_details.pop('host')
        except KeyError:
            pass

        initiator_details['reporting_level'] = "Initiator"

        return self.merge_dicts(initiator_details, initiator_perf_response)

    def get_wlp_compliance_details(self):
        """
        Gets all WLP Workload compliance information for a given VMAX.

        :return: list of dicts: all WLP workload compliance data
        """
        compliance_list = self.get_u4v_resource(method=GET,
                                                category='wlp',
                                                resource_type='symmetrix',
                                                resource_type_id=self.array_id,
                                                resource='compliance')

        comp_list = []
        for item in compliance_list['sloCompliance']:
            item['reporting_level'] = "WLP_Compliance"
            comp_list.append(self.merge_dicts(item))

        return comp_list

    def get_wlp_headroom_details(self):
        """
        Gets all WLP Headroom information for a given VMAX.

        :return: list of dicts: all WLP Headroom data
        """
        headroom_list = self.get_u4v_resource(method=GET,
                                              category='wlp',
                                              resource_type='symmetrix',
                                              resource_type_id=self.array_id,
                                              resource='headroom')

        headroom_response = []
        for item in headroom_list['headroom']:

            for k, v in item['processingDetails'].items():
                item[k] = v
            try:
                for k, v in item['headroomExpiry'].items():
                    item[('headroomExpiry_%(k)s' % {'k': k})] = v
                item.pop('headroomExpiry')
            except KeyError:
                pass

            item.pop('processingDetails')
            item.pop('nextUpdate')
            item['reporting_level'] = "WLP_Headroom"

            headroom_response.append(self.merge_dicts(item))

        return headroom_response


class Connector:
    def __init__(self, username=None, password=None, server_ip=None,
                 port=None, verify=None, array=None,
                 select_array=None, select_alerts=None, select_srp=None,
                 select_sg=None, select_director=None, select_port=None,
                 select_pg=None, select_host=None, select_initiator=None,
                 select_wlp=None, debug_enabled=None):

        self.username = username
        self.password = password
        self.server_ip = server_ip
        self.port = port
        self.verify = verify
        self.array = array

        self.select_array = select_array
        self.select_alerts = select_alerts
        self.select_srp = select_srp
        self.select_sg = select_sg
        self.select_director = select_director
        self.select_port = select_port
        self.select_pg = select_pg
        self.select_host = select_host
        self.select_initiator = select_initiator
        self.select_wlp = select_wlp
        self.debug_enabled = debug_enabled

        self.rf = RestFunctions(username=self.username, password=self.password,
                                server_ip=self.server_ip, port=self.port,
                                verify=self.verify, array=self.array,
                                debug_enabled=self.debug_enabled)

    def connector_runner(self):
        start_time = time.time()
        self.rf.validate_array()

        print("\tArray: %(array)s - Starting VMAX metrics collection run" % {
            'array': self.array
        })

        # Get Array level metrics
        if self.select_array:
            try:
                self.rf.get_array_summary(self.array)
            except TypeError:
                print("Array: %(array)s - There was an issue collecting "
                      "Array level metrics, please check status code for "
                      "further information. This may be a temporary Unisphere "
                      "response error which will clear itself." % {
                          'array': self.array})
            print("\tArray: %(array)s - Array metrics collected." %
                  {'array': self.array})

        # Get Alert info
        if self.select_alerts:
            try:
                for alert in self.rf.get_alert_list(symm_only=True):
                    try:
                        self.rf.get_symm_alert_details(alert)
                    except TypeError:
                        print("Array: %(array)s Alert: %(alert)s - There was "
                              "an issue collecting Alert metrics, please check "
                              "status code for further information. This may "
                              "be a temporary Unisphere response error which "
                              "will clear itself." % {
                                  'array': self.array,
                                  'alert': alert})
            except TypeError:
                print("Array: %(array)s - There was an issue collecting the "
                      "Alert ID list, please check status code for further "
                      "information. This may be a temporary Unisphere response "
                      "error which will clear itself." % {'array': self.array})
            print("\tArray: %(array)s - Alert metrics collected." %
                  {'array': self.array})

        # Get SRP info
        if self.select_srp:
            try:
                for srp in self.rf.get_srp_list():
                    try:
                        self.rf.get_srp_details(srp)
                    except TypeError:
                        print("Array: %(array)s SRP: %(srp)s - There was an "
                              "issue collecting SRP metrics, please check "
                              "status code for further information. This may "
                              "be a temporary Unisphere response error which "
                              "will clear itself." % {
                                  'array': self.array,
                                  'srp': srp})
            except TypeError:
                print("Array: %(array)s - There was an issue collecting the "
                      "SRP ID list, please check status code for further "
                      "information. This may be a temporary Unisphere response "
                      "error which will clear itself." % {'array': self.array})
            print("\tArray: %(array)s - SRP metrics collected." %
                  {'array': self.array})

        # Get SG info
        if self.select_sg:
            try:
                for sg in self.rf.get_sg_list():
                    try:
                        self.rf.get_sg_details(sg)
                    except TypeError:
                        print("Array: %(array)s SG: %(sg)s - There was an "
                              "issue collecting SG metrics, please check "
                              "status code for further information. This may "
                              "be a temporary Unisphere response error which "
                              "will clear itself." % {
                                  'array': self.array,
                                  'sg': sg})
            except TypeError:
                print("Array: %(array)s - There was an issue collecting the SG "
                      "ID list, please check status code for further "
                      "information. This may be a temporary Unisphere response "
                      "error which will clear itself." % {'array': self.array})
            print("\tArray: %(array)s - SG metrics collected." %
                  {'array': self.array})

        # Get Director info
        if self.select_director:
            try:
                for vmax_dir in self.rf.get_director_list():
                    try:
                        self.rf.get_director_details(vmax_dir)
                    except TypeError:
                        print("Array: %(array)s Director: %(vmax_dir)s - There "
                              "was an issue collecting Director metrics, "
                              "please check status code for further "
                              "information. This may be a temporary Unisphere "
                              "response error which will clear itself." % {
                                  'array': self.array,
                                  'vmax_dir': vmax_dir})
            except TypeError:
                print("Array: %(array)s - There was an issue collecting the "
                      "Director ID list, please check status code for further "
                      "information. This may be a temporary Unisphere response "
                      "error which will clear itself." % {'array': self.array})
            print("\tArray: %(array)s - Director metrics collected." %
                  {'array': self.array})

        # Get Port info
        if self.select_port:
            try:
                for port in self.rf.get_port_list():
                    try:
                        self.rf.get_port_details(port)
                    except TypeError:
                        print("Array: %(array)s Port: %(port)s - There was an "
                              "issue collecting Port metrics, please check "
                              "status code for further information. This may "
                              "be a temporary Unisphere response error which "
                              "will clear itself." % {
                                  'array': self.array,
                                  'port': port})
            except TypeError:
                print("Array: %(array)s - There was an issue collecting the "
                      "Port ID list, please check status code for further "
                      "information. This may be a temporary Unisphere response "
                      "error which will clear itself." % {'array': self.array})
            print("\tArray: %(array)s - Port metrics collected." %
                  {'array': self.array})

        # Get Port Group Info
        if self.select_pg:
            try:
                for pg in self.rf.get_pg_list():
                    try:
                        self.rf.get_pg_details(pg)
                    except TypeError:
                        dir_port = ("Dir:Port: %(dir)s:%(port)s" % {
                            'dir': pg['directorId'],
                            'port': pg['portId']
                        })
                        print("Array: %(array)s PG: %(dir_port)s - There was "
                              "an issue collecting PG metrics, please check "
                              "status code for further information. This may "
                              "be a temporary Unisphere response error "
                              "which will clear itself." % {
                                  'array': self.array,
                                  'dir_port': dir_port})
            except TypeError:
                print("Array: %(array)s - There was an issue collecting the "
                      "Port Group ID list, please check status code for "
                      "further information. This may be a temporary Unisphere "
                      "response error which will clear itself." %
                      {'array': self.array})
            print("\tArray: %(array)s - PG metrics collected." %
                  {'array': self.array})

        # Get Host info
        if self.select_host:
            try:
                summary_hosts, active_hosts = self.rf.get_host_list()
                for host in summary_hosts:
                    try:
                        self.rf.get_host_details(host, active_hosts)
                    except TypeError:
                        print("Array: %(array)s Host: %(host)s - There was an "
                              "issue collecting Host metrics, please check "
                              "status code for further information. This may "
                              "be a temporary Unisphere response error which "
                              "will clear itself." % {
                                  'array': self.array,
                                  'host': host})
            except TypeError:
                print("Array: %(array)s - There was an issue collecting the "
                      "Host ID list, please check status code for further "
                      "information. This may be a temporary Unisphere response "
                      "error which will clear itself." % {'array': self.array})
            print("\tArray: %(array)s - Host metrics collected." %
                  {'array': self.array})

        # Get Initiator info
        if self.select_initiator:
            try:
                summary_inits, active_inits = self.rf.get_initiator_list()
                for initiator in summary_inits:
                    try:
                        self.rf.get_initiator_details(initiator, active_inits)
                    except TypeError:
                        print("Array: %(array)s Initiator: %(initiator)s - "
                              "There was an issue collecting Initiator "
                              "metrics, please check status code for further "
                              "information. This may be a temporary Unisphere "
                              "response error which will clear itself." % {
                                  'array': self.array,
                                  'initiator': initiator})
            except TypeError:
                print("Array: %(array)s - There was an issue collecting the "
                      "Initiator ID list, please check status code for further "
                      "information. This may be a temporary Unisphere response "
                      "error which will clear itself." % {'array': self.array})
            print("\tArray: %(array)s - Initiator metrics collected." %
                  {'array': self.array})

        # Get WLP info
        if self.select_wlp:
            try:
                for _ in self.rf.get_wlp_compliance_details():
                    pass
            except TypeError:
                print("Array: %(array)s - There was an issue collecting "
                      "Compliance metrics, please check status code for "
                      "further information. This may be a temporary Unisphere "
                      "response error which will clear itself." % {
                          'array': self.array})
            print("\tArray: %(array)s - WLP Compliance metrics collected." %
                  {'array': self.array})

            try:
                for _ in self.rf.get_wlp_headroom_details():
                    pass
            except TypeError:
                print("Array: %(array)s - There was an issue collecting "
                      "Headroom metrics, please check status  code for further "
                      "information. This may be a temporary Unisphere response "
                      "error which will clear itself." % {
                          'array': self.array})
            print("\tArray: %(array)s - WLP Headroom metrics collected." %
                  {'array': self.array})

        end_time = time.time()
        print("\tArray: %(array)s - Finished metrics collection" % {
            'array': self.array})

        GLOBAL_TIMES[self.array] = end_time - start_time

        self.rf.close_session()


def main():
    def _str2bool(string):
        if str(string.lower()) == 'true':
            response = True
        elif str(string.lower()) == 'false':
            response = False
        else:
            response = string

        return response

    config = ConfigParser.ConfigParser()
    config.read('vmax_splunk_sizer_config.ini')

    u4v_enable_debug = config.get('DEBUG',
                                  'USER_ENABLE_DEBUG')
    u4v_ipaddress = config.get('ENVIRONMENT_SETTINGS',
                               'USER_U4V_IPADDRESS')
    u4v_port = config.get('ENVIRONMENT_SETTINGS',
                          'USER_U4V_PORT')
    u4v_username = config.get('ENVIRONMENT_SETTINGS',
                              'USER_U4V_USERNAME')
    u4v_password = config.get('ENVIRONMENT_SETTINGS',
                              'USER_U4V_PASSWORD')
    u4v_verify = _str2bool(config.get('ENVIRONMENT_SETTINGS',
                                      'USER_U4V_VERIFY'))
    u4v_arrays = config.get('ENVIRONMENT_SETTINGS',
                            'USER_U4V_ARRAYS')

    report_array = _str2bool(config.get('REPORTING_LEVELS',
                                        'USER_REPORT_ARRAY'))
    report_alerts = _str2bool(config.get('REPORTING_LEVELS',
                                         'USER_REPORT_ALERTS'))
    report_srp = _str2bool(config.get('REPORTING_LEVELS',
                                      'USER_REPORT_SRP'))
    report_sg = _str2bool(config.get('REPORTING_LEVELS',
                                     'USER_REPORT_SG'))
    report_director = _str2bool(config.get('REPORTING_LEVELS',
                                           'USER_REPORT_DIRECTOR'))
    report_port = _str2bool(config.get('REPORTING_LEVELS',
                                       'USER_REPORT_PORT'))
    report_pg = _str2bool(config.get('REPORTING_LEVELS',
                                     'USER_REPORT_PG'))
    report_host = _str2bool(config.get('REPORTING_LEVELS',
                                       'USER_REPORT_HOST'))
    report_init = _str2bool(config.get('REPORTING_LEVELS',
                                       'USER_REPORT_INITIATOR'))
    report_wlp = _str2bool(config.get('REPORTING_LEVELS',
                                      'USER_REPORT_WLP'))

    array_id_list = [x.strip() for x in u4v_arrays.split(',')]
    threads_num = int(len(array_id_list)) + 1
    my_threads = []

    print("#####################################")
    print("# VMAX for Splunk Environment Sizer #")
    print("# Version 2.0 - By Michael McAleer  #")
    print("#####################################")

    print("\nEnvironment Configuration:")
    print("\t-Unisphere IP/Host Address: %(u4v_address)s" % {
        'u4v_address': u4v_ipaddress})
    print("\t-Running Test for VMAX(s): %(list)s" % {
        'list': str(array_id_list)})
    print("\t-Debug Enabled: %(enabled)s" % {
        'enabled': str(u4v_enable_debug)})

    print("\nRunning VMAX for Splunk checks & metrics collection:")

    global_time_start = time.time()

    for array in array_id_list:
        running = False
        while not running:
            if threading.active_count() > threads_num:
                time.sleep(0.5)
            elif threading.active_count() < threads_num:
                conn = Connector(username=u4v_username,
                                 password=u4v_password,
                                 server_ip=u4v_ipaddress,
                                 port=u4v_port,
                                 verify=u4v_verify,
                                 array=array,
                                 select_array=report_array,
                                 select_alerts=report_alerts,
                                 select_srp=report_srp,
                                 select_sg=report_sg,
                                 select_director=report_director,
                                 select_port=report_port,
                                 select_pg=report_pg,
                                 select_host=report_host,
                                 select_initiator=report_init,
                                 select_wlp=report_wlp,
                                 debug_enabled=u4v_enable_debug)

                t = threading.Thread(target=conn.connector_runner)
                my_threads.append(t)
                t.start()
                running = True
                pass

    running = True
    while running:
        for thread in my_threads:
            if len(my_threads) >= 1:
                if thread.isAlive():
                    time.sleep(0.1)
                else:
                    my_threads.remove(thread)
                    if len(my_threads) == 0:
                        running = False
                        break

    global_time_finish = time.time()
    global_total_time = global_time_finish - global_time_start

    def _myround(x, base=300):
        response = int(base * round(float(x) / base))
        if response == 0:
            response = 300
        return response

    print("\n##########################")
    print("# Collection Run Results #")
    print("##########################")

    for array, run_time in GLOBAL_TIMES.iteritems():
        print(
                "Array %(array)s took %(time)s seconds to complete, the "
                "recommended reporting interval is %(interval)s seconds. The "
                "amount of calls completed was %(call_amount)s with an average "
                "time per call of %(avg_time)s" % {
                    'array': array,
                    'time': run_time,
                    'interval': _myround(run_time),
                    'call_amount': CALL_COUNT[array],
                    'avg_time': (run_time / int(CALL_COUNT[array]))
                })

    print("The entire metrics collection run took %(full_run)s seconds." % {
        'full_run': global_total_time
    })


main()
