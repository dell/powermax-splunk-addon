import json
import time
import sys
from rest_requests import RestRequests
from rest_keys_reformat import rename_dict

# HTTP constants
GET = 'GET'
POST = 'POST'
STATUS_200 = 200
STATUS_201 = 201
STATUS_202 = 202
STATUS_204 = 204


class RestFunctions:
    def __init__(self, username=None, password=None, server_ip=None,
                 port=None, verify=False, u4v_version='84', array=None,
                 rest_timeout=None, helper=None):

        base_url = "https://%s:%s/univmax/restapi" % (server_ip, port)
        self.rest_client = RestRequests(username, password, verify,
                                        base_url, rest_timeout, helper, array)
        self.request = self.rest_client.rest_request
        self.server_ip = server_ip
        self.array_id = array
        self.u4v_version = u4v_version
        self.helper = helper
        self.timestamp = None
        self.valid = self.validate_array()

    def make_request(self, target_uri, resource_type, method,
                     request_object=None,
                     params=None):
        """
        Make a REST request to U4V.

        :param target_uri: U4V REST target URI
        :param resource_type: the resource type e.g. storageGroup
        :param method: REST request type e.g. GET
        :param request_object: DICT for REST POST requests
        :param params: optional URL parameters to include in target URI
        :return: resource object -- dict or None
        """

        def _check_status_code_success(operation, status_code, message):
            """
            Check for successful status code of a given REST request.
            
            :param operation: the operation carried out e.g. GET storageGroup
            :param status_code: the status code returned from the REST request
            :param message: the message returned with the REST request
            :return: status message dependent on status code
            """
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
                    # If Unisphere returns a message return that message to
                    # user
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
                    # If Unisphere does not return a message, return HTTP
                    # response information if known in response_codes list
                    # above
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
            self.helper.log_error("Array: %(array)s - REST request failed." % {
                'array': self.array_id})
            exit("Exiting Metrics Run - Please check array connection.")

        rest_operation = '%(method)s %(res)s' % {
            'method': method,
            'res': resource_type}

        return_message = _check_status_code_success(rest_operation, sc,
                                                    response)
        if return_message:
            self.helper.log_error(
                "Array: %(array)s - REST request failed with: %(e)s" % {
                    'array': self.array_id,
                    'e': return_message})

        if sc == STATUS_200:
            resource_object = response
        return resource_object

    def get_u4v_resource(self, method, category, resource_type,
                         resource_type_id=None, resource=None,
                         resource_id=None, request_object=None,
                         port_id=None, params=None):
        """
        Get a given resource's information from U4V.

        :param method: the type of REST request e.g. GET
        :param category: the category of the U4V request e.g. sloprovisioning
        :param resource_type: the type of resource from the category
                              e.g. symmetrix
        :param resource_type_id: the ID of the resource type
        :param resource: the resource of the resource_type e.g. initiator
        :param resource_id: the ID of the resource
        :param request_object: DICT for REST POST requests
        :param port_id: the port ID if required for URI
        :param params: optional URL parameters to include in target URI
        :return: response object -- dict or None
        """

        target_uri = self.build_uri(category, resource_type,
                                    resource_type_id, resource,
                                    resource_id, port_id)

        return self.make_request(target_uri=target_uri,
                                 resource_type=resource_type,
                                 method=method, request_object=request_object,
                                 params=params)

    def close_session(self):
        """Close the current rest session.
        """
        self.rest_client.close_session()

    def build_uri(self, category, resource_type,
                  resource_type_id=None, resource=None,
                  resource_id=None, port_id=None):
        """
        Create the target URI given the specified arguments.

        :param category: the category of the U4V request e.g. sloprovisioning
        :param resource_type: the type of resource from the category
                              e.g. symmetrix
        :param resource_type_id: the ID of the resource type
        :param resource: the resource of the resource_type e.g. initiator
        :param resource_id: the ID of the resource
        :param port_id: the port ID if URI is for port info
        :return: U4V target URI - string
        """
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
        """
        Merge one or more dictionaries together.

        :param dict_args: dict object
        :return: single dictionary
        """

        result = {}
        for dictionary in dict_args:
            if dictionary is not None:
                result.update(dictionary)
            else:
                pass

        if result:
            import copy
            result_list_copy = copy.deepcopy(result)
            for k, v in result_list_copy.items():
                if k in ['arrayId', 'symmetrixId', 'symmId',
                         'timestamp', 'array']:
                    result.pop(k)

        result['timestamp'] = self.timestamp
        result['array_id'] = self.array_id
        self.rename_metrics(result)

        return json.dumps(result)

    @staticmethod
    def rename_metrics(payload):
        """
        Takes the combined payload for any given VMAX reporting level,
        parses through each key and changes it to a standardised format.
        If a a metric has no returned value, the value is set to 'N/A'.

        :param payload: The combined summary and performance metrics
                        payload for a given VMAX reporting level
        """

        for old_key in list(payload):
            if payload[old_key] == '':
                payload[old_key] = "N/A"
            for new_key in list(rename_dict):
                if old_key == new_key:
                    value = rename_dict[new_key]
                    payload[value] = payload.pop(old_key)

    def is_recent_timestamp(self):
        """
        Check is the array timestamp current as of 6 minutes ago.

        :return: boolean valid_timestamp, actual timestamp
        """

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
        try:
            if (current_timestamp - array_timestamp) < 540000:
                return True, array_timestamp
            else:
                return False, array_timestamp
        except TypeError:
            self.helper.log_critical(
                "Array: %(array)s - The request to URL extract the VMAX "
                "performance timestamp from Unisphere has failed. Please view "
                "previous VMAX TA logs and check your instance of Unisphere "
                "is accessible and responding as expected.") % {
                    'array': self.array_id}
            self.helper.log_critical("Array: %(array)s - Quit Collections Run "
                                     "due to Timestamp retrieval issue" % {
                                         'array': self.array_id})
            return False, array_timestamp

    def validate_array(self):
        """
        Perform the various validation checks to ensure VMAX is valid
        for performance and metrics stats collection. If any checks are not
        met metrics collection run will exit.

        Checks include:
        1. Check if Unisphere is responding
        2. Check if Unisphere meets required version
        3. Check if VMAX is VMAX-3 model or newer
        4. Check if VMAX is local & performance registered
        5. Check if VMAX performance timestamp is up-to-date

        :return: valid timestamp
        """
        u4v_version = self.get_u4v_resource(method='GET',
                                            category='system',
                                            resource_type='version')

        # Check if Unisphere is responding
        if not u4v_version:
            self.helper.log_critical(
                "Array: %(array)s - Unisphere not responding or is not "
                "required 8.4 version. Please check corresponding status code "
                "message above for further information. Is your VMAX data "
                "input configured correctly? (IP Address, port, username, "
                "password, SSL settings). Exiting metrics collection run." % {
                    'array': self.array_id})
            self.helper.log_critical("Array: %(array)s - Quit Collection Run" %
                                     {'array': self.array_id})
            return False

        self.helper.log_info(
            "Array: %(array)s - Check 1 Passed: U4V contact made." % {
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
            self.helper.log_critical(
                "Array: %(array)s - Unishphere is not v8.4.0.10 or newer "
                "version, please upgrade Unipshere to required version. "
                "Exiting metrics collection run." % {
                    'array': self.array_id})
            self.helper.log_critical(
                "Array: %(array)s - Quit Collections Run" % {
                    'array': self.array_id})
            return False

        self.helper.log_info(
            "Array: %(array)s - Check 2 Passed: U4V required 8.4.0.10 or "
            "newer." % {
                'array': self.array_id})

        # Check if VMAX is VMAX-3 model or newer
        isv3_response = self.get_u4v_resource(method='GET',
                                              category='sloprovisioning',
                                              resource_type='symmetrix',
                                              resource_type_id=self.array_id)

        if not isv3_response:
            self.helper.log_critical(
                "Array: %(array)s - VMAX-3 or newer array not found, please "
                "check array ID in data input configuration. Exiting metrics "
                "collection run." % {'array': self.array_id})
            self.helper.log_critical("Array: %(array)s - Quit Collections Run."
                                     % {'array': self.array_id})
            return False

        self.helper.log_info(
            "Array: %(array)s - Check 3 Passed: VMAX-3 or newer array "
            "found." % {'array': self.array_id})

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
            self.helper.log_critical(
                "Array: %(array)s - VMAX array not performance registered "
                "or is not local to Unisphere. Exiting metrics collection "
                "run." % {
                    'array': self.array_id})
            self.helper.log_critical(
                "Array: %(array)s - Quit Collections Run" % {
                    'array': self.array_id})
            return False

        self.helper.log_info(
            "Array: %(array)s - Check 4 Passed: VMAX array is performance "
            "registered." % {'array': self.array_id})

        # If performance registered, is timestamp up to date
        if isv3_response and perf_registered:
            time_true, timestamp = self.is_recent_timestamp()
            if time_true:
                self.timestamp = timestamp
                self.helper.log_info(
                    "Array: %(array)s - Check 5 Passed: VMAX Array "
                    "timestamp is up to date: %(timestamp)s." % {
                        'array': self.array_id,
                        'timestamp': self.timestamp})
                return True
            else:
                self.helper.log_critical(
                    "Array: %(array)s - VMAX array performance timestamp "
                    "%(timestamp)s not current. Exiting metrics collection "
                    "run." % {
                        'array': self.array_id,
                        'timestamp': timestamp})
                self.helper.log_critical("Array: %(array)s - Quit Collections "
                                         "Run" % {'array': self.array_id})
                return False

    def get_array_summary(self, array_id):
        """
        Get all array level details for the following reporting levels:
        summary, system, WLP, migration, replication details, replication
        capabilities, alert summary, performance details.

        :param array_id: VMAX numerical ID
        :return: combined JSON response of all summary & performance data
        """
        # Get array summary details
        array_summary_return = self.get_u4v_resource(
            method=GET, category='sloprovisioning',
            resource_type='symmetrix',
            resource_type_id=array_id)

        # If array summary response remove nested dicts key:values to top level
        # of response and remove nested dicts
        if array_summary_return:
            for k, v in array_summary_return['sloCompliance'].items():
                array_summary_return[('sloCompliance_%(k)s' % {'k': k})] = v
            for k, v in array_summary_return['physicalCapacity'].items():
                array_summary_return[
                    ('physicalCapacity_%(k)s' % {'k': k})] = v
            array_summary_return.pop('sloCompliance')
            array_summary_return.pop('physicalCapacity')
        else:
            array_summary_return['array_summary_details'] = False
            array_summary_return['array_summary_message'] = \
                "No Array summary info data available"

        # Get array system details
        array_system_return = self.get_u4v_resource(method=GET,
                                                    category='system',
                                                    resource_type='symmetrix',
                                                    resource_type_id=array_id)

        if not array_system_return:
            array_system_return['array_system_details'] = False
            array_system_return['array_system_message'] = \
                "No Array system summary data available"

        # Get array WLP summary
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

        # Get array migration summary
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

        # Get array replication details
        array_rep_cap_response = self.get_u4v_resource(
            method=GET, category='replication',
            resource_type='capabilities',
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

        # Get array replication details
        array_replication_return = self.get_u4v_resource(
            method=GET, category='replication', resource_type='symmetrix',
            resource_type_id=array_id)

        if not array_replication_return:
            array_replication_return = dict()
            array_replication_return['array_replication_details'] = False
            array_replication_return['array_replication_message'] = \
                "No Array replication summary data available"

        # Get Array Alert Summary
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
                        aar[('performanceAlertSummary_%(k)s' % {
                            'k': k})] = v
                    aar.pop('performanceAlertSummary')
                    for k, v in aar['arrayAlertSummary'].items():
                        aar[('arrayAlertSummary_%(k)s' % {'k': k})] = v
                    aar.pop('arrayAlertSummary')
        if not found_symm:
            aar['array_alert_details'] = False
            aar['array_alert_message'] = \
                "No Array alerts summary data available"

        # Get array performance details
        array_perf_payload = {
            'startDate': str(self.timestamp),
            'symmetrixId': self.array_id,
            'metrics': [
                'CriticalAlertCount', 'InfoAlertCount', 'WarningAlertCount',
                'AllocatedCapacity', 'AvgFallThruTime', 'Cache_Balance',
                'DA_Balance', 'DX_Balance', 'EFD_Balance', 'FC_Balance',
                'FE_Balance', 'RDF_Balance', 'SATA_Balance', 'BEIOs',
                'BEReadReqs', 'BEUtilization', 'BEWriteReqs', 'BEReqs',
                'OverallCompressionRatio', 'CopySlotCount',
                'DeviceWPEvents',
                'OverallEfficiencyRatio', 'FEReadReqs', 'FEUtilization',
                'FEWriteReqs', 'HostMBs', 'FEHitReqs',
                'HardwareHealthScore',
                'HostIOs', 'HostMBReads', 'HostMBWritten',
                'DiskUtilization',
                'AvgOptimizedReadMissSize', 'OptimizedMBReadMisses',
                'OptimizedReadMisses', 'OverallHealthScore',
                'FEWriteMissReqs',
                'PercentEffectiveUsedCapacity', 'PercentHit', 'WPCount',
                'PercentMetaRepUsed', 'PercentMetaSystemUsed', 'FEReqs',
                'PercentReads', 'PercentSnapshotSaved',
                'VPCompressionRatio',
                'PercentSubscribedCapacity', 'PercentVPSaved',
                'PercentWrites',
                'PrefetchedTracks', 'QueueDepthUtilization', 'RDFA_WPCount',
                'RDFUtilization', 'FEReadHitReqs', 'FEReadMissReqs',
                'SloHealthScore', 'SnapshotCompressionRatio', 'HostReads',
                'SnapshotEfficiencyRatio', 'SnapshotSharedRatio',
                'SubscribedCapacity', 'SoftwareHealthScore',
                'SystemWPEvents',
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
            array_perf_return = array_perf_response['resultList']['result'][
                0]
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
        """
        Gets all alerts from instance of Unisphere associated with VMAX. If
        symm_only is True, only alerts with the associated array_id in the
        alert description will be returned, otherwise all alerts from that
        instance of Unisphere are returned regardless of its respective
        array.

        :param symm_only: Boolean: True/False
        :return: List of Unisphere alert IDs
        """

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
        """
        Get all alert details for a given alert ID.

        :param alert_id: the alert ID
        :return: dict: alert details
        """
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

        self.rename_metrics(array_alert_details)
        return json.dumps(array_alert_details)

    def get_srp_list(self):
        """
        Get a list of all SRPs in a given VMAX.

        :return: list: list of SRPs
        """
        array_srp_details = self.get_u4v_resource(
            method=GET, category='sloprovisioning',
            resource_type='symmetrix',
            resource_type_id=self.array_id, resource='srp')

        return array_srp_details['srpId']

    def get_srp_details(self, srp_id):
        """
        Get all SRP details for a given SRP.

        :param srp_id: the SRP ID
        :return: dict: SRP details
        """
        srp_details = self.get_u4v_resource(method=GET,
                                            category='sloprovisioning',
                                            resource_type='symmetrix',
                                            resource_type_id=self.array_id,
                                            resource='srp',
                                            resource_id=srp_id)
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
                'OverallEfficiencyRatio', 'HostMBs', 'HostIOs',
                'HostMBReads',
                'PercentSnapshotSaved', 'SnapshotEfficiencyRatio', 'BEReqs',
                'PercentVPSaved', 'HostReads', 'ResponseTime', 'HostWrites',
                'VPSharedRatio', 'ReadResponseTime', 'WriteResponseTime',
                'SnapshotSharedRatio', 'TotalSRPCapacity',
                'UsedSRPCapacity',
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
                                srp_perf_response['resultList']['result'][
                                    0])

    def get_sg_list(self):
        """
        Get a list of all SGs in a given VMAX.

        :return: list: list of SGs
        """
        array_sg_details = self.get_u4v_resource(
            method=GET, category='sloprovisioning',
            resource_type='symmetrix',
            resource_type_id=self.array_id, resource='storagegroup')

        return array_sg_details['storageGroupId']

    def get_sg_details(self, sg_id):
        """
        Get all SRP details for a given SRP.

        :param sg_id: the SG ID
        :return: dict: SG details
        """
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
                'AllocatedCapacity', 'TotalTracks',
                'BEDiskReadResponseTime',
                'BEReadRequestTime', 'BEReadTaskTime', 'AvgIOSize',
                'AvgReadResponseTime6', 'AvgReadResponseTime7',
                'AvgReadSize',
                'AvgWritePacedDelay', 'AvgWriteResponseTime6',
                'AvgWriteSize',
                'AvgWriteResponseTime7', 'BEMBReads', 'BEMBTransferred',
                'BEPercentReads', 'BEMBWritten', 'BEPercentWrites',
                'BEPrefetchedTrackss', 'BEPrefetchedTrackUsed',
                'BEReadReqs',
                'BEWriteReqs', 'CompressedTracks', 'CompressionRatio',
                'BlockSize', 'HostMBs', 'IODensity', 'HostIOs',
                'RdfReadHits',
                'MaxWPThreshold', 'HostMBReads', 'HostMBWritten',
                'RdfReads',
                'PercentCompressedTracks', 'PercentHit', 'PercentMisses',
                'PercentRandomIO', 'PercentRandomReads', 'PercentRead',
                'PercentRandomReadHit', 'PercentRandomReadMiss',
                'RdfMBRead',
                'PercentRandomWrites', 'PercentRandomWriteHit',
                'RdfMBWritten',
                'PercentRandomWriteMiss', 'PercentReadHit',
                'PercentReadMiss',
                'PercentSeqRead', 'PercentSeqIO', 'PercentSeqReadHit',
                'PercentSeqReadMiss', 'PercentSeqWrites',
                'PercentSeqWriteHit',
                'PercentSeqWriteMiss', 'PercentVPSpaceSaved',
                'PercentWrite',
                'PercentWriteHit', 'PercentWriteMiss', 'BEPrefetchedMBs',
                'HostIOLimitPercentTimeExceeded', 'RandomIOs',
                'HostReadHits',
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
                'SeqWriteHits', 'SeqWriteMisses', 'SeqWrites',
                'SRDFA_MBSent',
                'SRDFA_WriteReqs', 'SRDFS_MBSent', 'SRDFS_WriteReqs',
                'BEReqs',
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
            method=POST, category='performance',
            resource_type='StorageGroup',
            resource='metrics', request_object=sg_perf_payload)

        sg_details['reporting_level'] = "SG"

        return self.merge_dicts(sg_details,
                                srp_perf_response['resultList']['result'][
                                    0])

    def get_director_list(self):
        """
        Get a list of all Directors in a given VMAX.

        :return: list: list of Directors
        """
        array_director_list = self.get_u4v_resource(
            method=GET, category='sloprovisioning',
            resource_type='symmetrix',
            resource_type_id=self.array_id, resource='director')

        return array_director_list['directorId']

    def get_director_details(self, director_id):
        """
        Get all Director details for a given Director. The director details
        returned are dependent on the Director prefix which denotes the
        director type.

        :param director_id: the Director ID
        :return: dict: Director details
        """
        array_director_details = self.get_u4v_resource(
            method=GET, category='sloprovisioning',
            resource_type='symmetrix',
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
                    'AvgTimePerSyscall', 'CompressedMBs',
                    'CompressedReadMBs',
                    'CompressedWriteMBs', 'CompressedReadReqs', 'MBWritten',
                    'CompressedReqs', 'CompressedWriteReqs', 'IOs', 'MBs',
                    'MBRead', 'PercentBusy', 'PercentBusyLogicalCore_0',
                    'PercentBusyLogicalCore_1', 'PercentNonIOBusy',
                    'PercentNonIOBusyLogicalCore_0', 'Syscall_RDF_DirCount',
                    'PercentNonIOBusyLogicalCore_1', 'PercentReadReqs',
                    'PercentWriteReqs', 'PrefetchedTracks', 'ReadReqs',
                    'Reqs',
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
                    'OptimizedReadMisses', 'PercentBusy',
                    'PercentWriteReqs',
                    'PercentBusyLogicalCore_0', 'PercentBusyLogicalCore_1',
                    'PercentHitReqs', 'PercentReadReqs',
                    'PercentReadReqHit',
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
                    'ReadRTCountRange8To16', 'ReadRTCountRangeover64',
                    'Reqs',
                    'ReadResponseTime', 'WriteResponseTime',
                    'SlotCollisions',
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
                    'AvgIOServiceTime', 'AvgIOSizeReceived',
                    'AvgIOSizeSent',
                    'AvgTimePerSyscall', 'CompresedMBSentAndReceived',
                    'CompresedMBReceived', 'CompresedMBSent', 'CopyIOs',
                    'CopyMBs', 'IOs', 'MBSentAndReceived', 'MBRead',
                    'MBWritten', 'NumberOfCompresedLinks', 'PercentBusy',
                    'NumberOfLinks', 'PercentCompresedMBSentAndReceived',
                    'PercentCompresedMBReceived', 'PercentCompresedMBSent',
                    'Reqs', 'Rewrites', 'AsyncMBSent', 'AsyncWriteReqs',
                    'SyncWrites', 'SyscallCount', 'SyncMBSent',
                    'SyscallTime',
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
        """
        Get a list of all Port Groups in a given VMAX.

        :return: list: list of Port Groups
        """
        array_pg_list = self.get_u4v_resource(method=GET,
                                              category='sloprovisioning',
                                              resource_type='symmetrix',
                                              resource_type_id=self.array_id,
                                              resource='portgroup')
        return array_pg_list['portGroupId']

    def get_pg_details(self, pg_id):
        """
        Get all Port Group details for a given Port Group.

        :param pg_id: the Port Group ID
        :return: dict: Port Group details
        """
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
        """
        Get a list of all Ports in a given VMAX.

        :return: list: list of Ports
        """
        array_port_list = self.get_u4v_resource(method=GET,
                                                category='sloprovisioning',
                                                resource_type='symmetrix',
                                                resource_type_id=self.array_id,
                                                resource='port')
        return array_port_list['symmetrixPortKey']

    def get_port_details(self, port_key):
        """
        Get all Port details for a given Port.

        :param port_key: the Director:Port ID combination
        :return: dict: Port details
        """
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
                    'MBWritten', 'PercentBusy', 'Reads', 'SpeedGBs',
                    'Writes'
                ],
                'directorId': director_id,
                'dataFormat': "Average",
                'endDate': self.timestamp,
                'portId': port_id
            }

            port_perf_response = self.get_u4v_resource(
                method=POST, category='performance',
                resource_type='RDFPort',
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

        return self.merge_dicts(port_details['symmetrixPort'],
                                port_response)

    def get_host_list(self):
        """
        Get a list of all Hosts in a given VMAX.

        :return: list: list of Hosts
        """
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
        """
        Get all Host details for a given Host.

        :param host_id: the Host ID
        :param active_host_list: list of active hosts
        :return:
        """

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

            host_perf_response = host_perf_response['resultList']['result'][
                0]
        else:
            host_details['host_perf_details'] = False
            host_details['host_perf_message'] = \
                "No active Host performance data available"

        host_details['reporting_level'] = "Host"

        return self.merge_dicts(host_details, host_perf_response)

    def get_initiator_list(self):
        """
        Get a list of all Initiators associated with a given VMAX

        :return: list: list of Initiators
        """
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
        """
        Get all Initiator details for a given Initiator.

        :param initiator_id: the Initiator ID
        :param active_initiator_list: list of active initiators
        :return: dict: Host details
        """

        initiator_details = self.get_u4v_resource(
            method=GET, category='sloprovisioning',
            resource_type='symmetrix',
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
                    resource='metrics',
                    request_object=initiator_perf_payload)

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
        if not compliance_list:
            compliance_list = self.get_u4v_resource(
                method=GET, category='wlp', resource_type='symmetrix',
                resource_type_id=self.array_id, resource='compliancehistory')

        comp_list = []
        if compliance_list:
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
